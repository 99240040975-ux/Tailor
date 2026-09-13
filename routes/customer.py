from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from models import db
from models.message import Message
from models.measurement import Measurement
from models.order import Order
from models.review import Review
from models.tailor import Tailor
from models.user import User
from utils.decorators import customer_required
from utils.file_upload import save_uploaded_file


customer_bp = Blueprint("customer", __name__)


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

@customer_bp.route("/dashboard")
@login_required
@customer_required
def dashboard():
    active_orders = (
        Order.query
        .filter(
            Order.customer_id == current_user.id,
            Order.status != "delivered",
            Order.status != "cancelled",
        )
        .order_by(Order.updated_at.desc())
        .all()
    )

    completed_orders = (
        Order.query
        .filter_by(
            customer_id=current_user.id,
            status="delivered",
        )
        .count()
    )

    measurement_count = (
        Measurement.query
        .filter_by(customer_id=current_user.id)
        .count()
    )

    top_tailors = (
        Tailor.query
        .filter(
            Tailor.is_active.is_(True),
        )
        .order_by(
            Tailor.rating.desc(),
            Tailor.total_reviews.desc(),
        )
        .limit(4)
        .all()
    )

    return render_template(
        "customer/dashboard.html",
        active_orders=active_orders,
        completed_orders=completed_orders,
        measurement_count=measurement_count,
        top_tailors=top_tailors,
    )


# ------------------------------------------------------------
# Customer profile
# ------------------------------------------------------------

@customer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@customer_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if name:
            current_user.name = name

        current_user.phone = phone

        # The rebuilt User model currently does not contain a
        # profile_pic column, so uploaded profile images are not
        # assigned to the User model here.
        #
        # We still accept the upload so existing forms do not
        # break. The upload helper may save it for future use.
        profile_pic = request.files.get("profile_pic")

        if profile_pic and profile_pic.filename:
            save_uploaded_file(
                profile_pic,
                folder_name="profile",
            )

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success",
        )

        return redirect(
            url_for("customer.profile")
        )

    return render_template(
        "customer/profile.html"
    )


# ------------------------------------------------------------
# Tailor discovery
# ------------------------------------------------------------

@customer_bp.route("/tailors")
def tailors():
    """
    Discover active local tailors.

    The current Tailor model stores city/address as text.
    Location hierarchy filtering remains supported through
    the free-text city search until dedicated location IDs
    are added back to the Tailor model.
    """

    search_q = request.args.get(
        "q",
        "",
    ).strip()

    district_id = request.args.get(
        "district_id",
        type=int,
    )

    taluk_id = request.args.get(
        "taluk_id",
        type=int,
    )

    city_id = request.args.get(
        "city_id",
        type=int,
    )

    town_id = request.args.get(
        "town_id",
        type=int,
    )

    village_id = request.args.get(
        "village_id",
        type=int,
    )

    specialization = request.args.get(
        "specialization",
        "",
    ).strip()

    city = request.args.get(
        "city",
        "",
    ).strip()

    min_rating = request.args.get(
        "min_rating",
        type=float,
    )

    available_only = (
        request.args.get("available") == "1"
    )

    sort = request.args.get(
        "sort",
        "rating_desc",
    )

    query = Tailor.query.filter(
        Tailor.is_active.is_(True)
    )

    # Location hierarchy filtering
    if district_id:
        query = query.filter(Tailor.district_id == district_id)

    if taluk_id:
        query = query.filter(Tailor.taluk_id == taluk_id)

    if city_id:
        query = query.filter(Tailor.city_id == city_id)

    if town_id:
        query = query.filter(Tailor.town_id == town_id)

    if village_id:
        query = query.filter(Tailor.village_id == village_id)

    # General search
    if search_q:
        search_pattern = f"%{search_q}%"

        query = query.filter(
            db.or_(
                Tailor.shop_name.ilike(search_pattern),
                Tailor.specialization.ilike(search_pattern),
                Tailor.description.ilike(search_pattern),
                Tailor.city.ilike(search_pattern),
                Tailor.address.ilike(search_pattern),
            )
        )

    location_q = request.args.get(
        "location_q",
        "",
    ).strip()

    # Live Tamil Nadu location search (typed place name)
    if location_q:
        from models.location import District, Taluk, City, Town, Village
        loc_pat = f"%{location_q}%"
        query = query.filter(
            db.or_(
                Tailor.city.ilike(loc_pat),
                Tailor.address.ilike(loc_pat),
                Tailor.district.has(District.name.ilike(loc_pat)),
                Tailor.taluk.has(Taluk.name.ilike(loc_pat)),
                Tailor.city_rel.has(City.name.ilike(loc_pat)),
                Tailor.town.has(Town.name.ilike(loc_pat)),
                Tailor.village.has(Village.name.ilike(loc_pat)),
            )
        )

    # City search
    if city:
        query = query.filter(
            Tailor.city.ilike(f"%{city}%")
        )

    # Specialization
    if specialization:
        query = query.filter(
            Tailor.specialization.ilike(
                f"%{specialization}%"
            )
        )

    # Minimum rating
    if min_rating is not None:
        query = query.filter(
            Tailor.rating >= min_rating
        )

    # Availability is stored as text in the rebuilt model.
    if available_only:
        query = query.filter(
            db.func.lower(
                db.func.coalesce(
                    Tailor.availability,
                    "",
                )
            ).in_(
                [
                    "available",
                    "open",
                    "yes",
                    "true",
                ]
            )
        )

    # Sorting
    if sort == "experience_desc":
        query = query.order_by(
            Tailor.experience.desc(),
            Tailor.rating.desc(),
        )

    elif sort == "reviews_desc":
        query = query.order_by(
            Tailor.total_reviews.desc(),
            Tailor.rating.desc(),
        )

    elif sort == "newest":
        query = query.order_by(
            Tailor.created_at.desc()
        )

    else:
        query = query.order_by(
            Tailor.rating.desc(),
            Tailor.total_reviews.desc(),
        )

    tailors_list = query.all()

    # Tamil Nadu districts for the location selector.
    districts = []

    try:
        from models.location import District, State

        tn_state = (
            State.query
            .filter(
                db.or_(
                    State.code.ilike("TN"),
                    State.code.ilike("33"),
                    State.name.ilike("Tamil Nadu"),
                )
            )
            .first()
        )

        if tn_state:
            districts = (
                District.query
                .filter_by(state_id=tn_state.id)
                .order_by(District.name.asc())
                .all()
            )

    except Exception:
        districts = []

    return render_template(
        "customer/tailors.html",
        tailors=tailors_list,
        districts=districts,
        search_q=search_q,
        location_q=location_q,
        selected_city=city,
        selected_spec=specialization,
        selected_sort=sort,
        available_only=available_only,
        selected_district=district_id,
        selected_taluk=taluk_id,
    )


# ------------------------------------------------------------
# Tailor details
# ------------------------------------------------------------

@customer_bp.route("/tailors/<int:tailor_id>")
def tailor_details(tailor_id):
    tailor = Tailor.query.get_or_404(
        tailor_id
    )

    reviews = (
        Review.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "customer/tailor_details.html",
        tailor=tailor,
        reviews=reviews,
    )


# ------------------------------------------------------------
# Messages
# ------------------------------------------------------------

@customer_bp.route("/messages", methods=["GET"])
@login_required
def messages():
    order_id = request.args.get(
        "order_id",
        type=int,
    )

    recipient_id = request.args.get(
        "user_id",
        type=int,
    )

    sent_ids = (
        db.session.query(Message.receiver_id)
        .filter_by(
            sender_id=current_user.id
        )
    )

    received_ids = (
        db.session.query(Message.sender_id)
        .filter_by(
            receiver_id=current_user.id
        )
    )

    contact_ids = {
        row[0]
        for row in sent_ids.union(received_ids).all()
    }

    contacts = (
        User.query
        .filter(User.id.in_(contact_ids))
        .order_by(User.name.asc())
        .all()
        if contact_ids
        else []
    )

    active_contact = None
    chat_messages = []
    active_order = None

    # --------------------------------------------------------
    # Active order
    # --------------------------------------------------------

    if order_id:
        active_order = (
            Order.query
            .filter_by(id=order_id)
            .first()
        )

        # Customers may only open their own orders.
        if (
            active_order
            and active_order.customer_id
            != current_user.id
        ):
            active_order = None

    if active_order:
        tailor = active_order.tailor

        if tailor and tailor.user:
            active_contact = tailor.user

    # --------------------------------------------------------
    # Explicit recipient
    # --------------------------------------------------------

    if not active_contact and recipient_id:
        candidate = User.query.get(
            recipient_id
        )

        if candidate and candidate.id != current_user.id:
            active_contact = candidate

    # --------------------------------------------------------
    # First available conversation
    # --------------------------------------------------------

    if not active_contact and contacts:
        active_contact = contacts[0]

    # --------------------------------------------------------
    # Load conversation
    # --------------------------------------------------------

    if active_contact:
        conversation_filter = db.or_(
            db.and_(
                Message.sender_id == current_user.id,
                Message.receiver_id == active_contact.id,
            ),
            db.and_(
                Message.sender_id == active_contact.id,
                Message.receiver_id == current_user.id,
            ),
        )

        query = Message.query.filter(
            conversation_filter
        )

        if order_id:
            query = query.filter(
                db.or_(
                    Message.order_id == order_id,
                    Message.order_id.is_(None),
                )
            )

        chat_messages = (
            query
            .order_by(Message.created_at.asc())
            .all()
        )

        # Mark only this conversation's received
        # messages as read.
        (
            Message.query
            .filter(
                Message.sender_id == active_contact.id,
                Message.receiver_id == current_user.id,
                Message.is_read == False,
            )
            .update(
                {"is_read": True},
                synchronize_session=False,
            )
        )

        db.session.commit()

    return render_template(
        "customer/messages.html",
        contacts=contacts,
        active_contact=active_contact,
        active_order=active_order,
        chat_messages=chat_messages,
    )


# ------------------------------------------------------------
# Send message
# ------------------------------------------------------------

@customer_bp.route(
    "/messages/send",
    methods=["POST"],
)
@login_required
def send_message():
    receiver_id = request.form.get(
        "receiver_id",
        type=int,
    )

    order_id = request.form.get(
        "order_id",
        type=int,
    )

    message_text = request.form.get(
        "message",
        "",
    ).strip()

    if not receiver_id:
        flash(
            "Please select a recipient.",
            "danger",
        )
        return redirect(
            request.referrer
            or url_for("customer.messages")
        )

    if receiver_id == current_user.id:
        flash(
            "You cannot send a message to yourself.",
            "danger",
        )
        return redirect(
            request.referrer
            or url_for("customer.messages")
        )

    if not message_text:
        flash(
            "Message text cannot be empty.",
            "danger",
        )
        return redirect(
            request.referrer
            or url_for("customer.messages")
        )

    receiver = User.query.get(receiver_id)

    if not receiver or not receiver.is_active:
        flash(
            "The selected user is not available.",
            "danger",
        )
        return redirect(
            request.referrer
            or url_for("customer.messages")
        )

    # If an order is supplied, make sure it belongs to
    # the logged-in customer.
    if order_id:
        order = (
            Order.query
            .filter_by(
                id=order_id,
                customer_id=current_user.id,
            )
            .first()
        )

        if not order:
            flash(
                "Invalid order selected.",
                "danger",
            )
            return redirect(
                request.referrer
                or url_for("customer.messages")
            )

    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        order_id=order_id or None,
        message=message_text,
        is_read=False,
    )

    db.session.add(message)
    db.session.commit()

    flash(
        "Message sent!",
        "success",
    )

    return redirect(
        url_for(
            "customer.messages",
            user_id=receiver_id,
            order_id=order_id,
        )
    )