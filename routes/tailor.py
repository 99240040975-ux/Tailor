from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.message import Message
from models.order import Order
from models.review import Review
from models.tailor import Tailor
from utils.decorators import tailor_required
from utils.file_upload import save_uploaded_file


tailor_bp = Blueprint("tailor", __name__)


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

@tailor_bp.route("/dashboard")
@login_required
@tailor_required
def dashboard():
    tailor = current_user.tailor_profile

    if not tailor:
        flash(
            "Please complete your tailor profile.",
            "warning",
        )
        return redirect(
            url_for("tailor.edit_profile")
        )

    orders = (
        Order.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    pending_count = sum(
        1 for order in orders
        if order.status == "pending"
    )

    active_statuses = {
        "confirmed",
        "cutting",
        "stitching",
        "alteration",
        "quality_check",
    }

    active_count = sum(
        1 for order in orders
        if order.status in active_statuses
    )

    ready_count = sum(
        1 for order in orders
        if order.status == "ready"
    )

    completed_count = sum(
        1 for order in orders
        if order.status == "delivered"
    )

    total_revenue = sum(
        float(order.quotation or 0)
        for order in orders
        if order.status == "delivered"
        and order.quotation is not None
    )

    recent_orders = orders[:6]

    recent_reviews = (
        Review.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Review.created_at.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "tailor/dashboard.html",
        tailor=tailor,
        pending_count=pending_count,
        active_count=active_count,
        ready_count=ready_count,
        completed_count=completed_count,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        recent_reviews=recent_reviews,
    )


# ------------------------------------------------------------
# Tailor profile
# ------------------------------------------------------------

@tailor_bp.route("/profile")
@login_required
@tailor_required
def profile():
    tailor = current_user.tailor_profile

    if not tailor:
        return redirect(
            url_for("tailor.edit_profile")
        )

    reviews = (
        Review.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "tailor/profile.html",
        tailor=tailor,
        reviews=reviews,
    )


# ------------------------------------------------------------
# Edit tailor profile
# ------------------------------------------------------------

@tailor_bp.route(
    "/edit_profile",
    methods=["GET", "POST"],
)
@login_required
@tailor_required
def edit_profile():
    tailor = current_user.tailor_profile

    if not tailor:
        tailor = Tailor(
            user_id=current_user.id,
            shop_name=(
                f"{current_user.name}'s Tailoring"
            ),
            specialization=(
                "Custom Tailoring & Alterations"
            ),
            availability="Available",
            is_active=True,
            is_verified=False,
        )

        db.session.add(tailor)
        db.session.commit()

    if request.method == "POST":
        shop_name = request.form.get(
            "shop_name",
            "",
        ).strip()

        specialization = request.form.get(
            "specialization",
            "",
        ).strip()

        city = request.form.get(
            "city",
            "",
        ).strip()

        address = request.form.get(
            "address",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        price_range = request.form.get(
            "price_range",
            "",
        ).strip()

        tailor.shop_name = (
            shop_name or tailor.shop_name
        )

        tailor.specialization = (
            specialization
            or "Custom Tailoring & Alterations"
        )

        tailor.city = city or None
        tailor.address = address or None
        tailor.description = description or None
        tailor.price_range = price_range or None

        experience_value = request.form.get(
            "experience",
            "",
        ).strip()

        if experience_value:
            try:
                experience = int(experience_value)

                if experience >= 0:
                    tailor.experience = experience

            except ValueError:
                flash(
                    "Experience must be a valid number.",
                    "warning",
                )

        # The rebuilt Tailor model stores availability as text.
        availability_value = request.form.get(
            "availability",
            "",
        ).strip().lower()

        if availability_value in {
            "available",
            "open",
            "yes",
            "true",
            "1",
        }:
            tailor.availability = "Available"

        elif availability_value in {
            "unavailable",
            "closed",
            "no",
            "false",
            "0",
        }:
            tailor.availability = "Unavailable"

        elif availability_value:
            tailor.availability = (
                request.form.get(
                    "availability",
                    "",
                ).strip()
            )

        # Preserve the existing profile upload behavior
        # without assigning a non-existent profile_pic field
        # to the User model.
        profile_pic = request.files.get(
            "profile_pic"
        )

        if profile_pic and profile_pic.filename:
            save_uploaded_file(
                profile_pic,
                folder_name="profile",
            )

        db.session.commit()

        flash(
            "Studio profile updated successfully!",
            "success",
        )

        return redirect(
            url_for("tailor.profile")
        )

    return render_template(
        "tailor/edit_profile.html",
        tailor=tailor,
    )


# ------------------------------------------------------------
# Tailor orders
# ------------------------------------------------------------

@tailor_bp.route("/orders")
@login_required
@tailor_required
def orders():
    tailor = current_user.tailor_profile

    if not tailor:
        return redirect(
            url_for("tailor.edit_profile")
        )

    status_filter = request.args.get(
        "status",
        "all",
    ).strip()

    query = Order.query.filter_by(
        tailor_id=tailor.id
    )

    if (
        status_filter != "all"
        and status_filter in Order.STATUS_FLOW
    ):
        query = query.filter_by(
            status=status_filter
        )
    else:
        status_filter = "all"

    orders_list = (
        query
        .order_by(Order.updated_at.desc())
        .all()
    )

    return render_template(
        "tailor/orders.html",
        orders=orders_list,
        status_filter=status_filter,
        stages=list(Order.STATUS_LABELS.items()),
        status_labels=Order.STATUS_LABELS,
    )


# ------------------------------------------------------------
# Order details
# ------------------------------------------------------------

@tailor_bp.route(
    "/orders/<int:order_id>"
)
@login_required
@tailor_required
def order_details(order_id):
    tailor = current_user.tailor_profile

    if not tailor:
        return redirect(
            url_for("tailor.edit_profile")
        )

    order = (
        Order.query
        .filter_by(
            id=order_id,
            tailor_id=tailor.id,
        )
        .first_or_404()
    )

    return render_template(
        "tailor/order_details.html",
        order=order,
        stages=list(Order.STATUS_LABELS.items()),
        status_labels=Order.STATUS_LABELS,
    )


# ------------------------------------------------------------
# Quotations
# ------------------------------------------------------------

@tailor_bp.route("/quotations")
@login_required
@tailor_required
def quotations():
    tailor = current_user.tailor_profile

    if not tailor:
        return redirect(
            url_for("tailor.edit_profile")
        )

    pending_quotes = (
        Order.query
        .filter_by(
            tailor_id=tailor.id,
            status="pending",
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    quoted_orders = (
        Order.query
        .filter_by(
            tailor_id=tailor.id,
            status="quoted",
        )
        .order_by(Order.updated_at.desc())
        .all()
    )

    return render_template(
        "tailor/quotations.html",
        pending_quotes=pending_quotes,
        quoted_orders=quoted_orders,
    )


# ------------------------------------------------------------
# Tailor messaging
# ------------------------------------------------------------

@tailor_bp.route("/messages")
@login_required
@tailor_required
def messages():
    return redirect(
        url_for("customer.messages")
    )


# ------------------------------------------------------------
# Reviews
# ------------------------------------------------------------

@tailor_bp.route("/reviews")
@login_required
@tailor_required
def reviews():
    tailor = current_user.tailor_profile

    if not tailor:
        return redirect(
            url_for("tailor.edit_profile")
        )

    reviews_list = (
        Review.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "tailor/reviews.html",
        tailor=tailor,
        reviews=reviews_list,
    )