from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.order import Order
from models.review import Review
from models.tailor import Tailor
from models.user import User
from utils.decorators import admin_required


admin_bp = Blueprint("admin", __name__)


# ------------------------------------------------------------
# Admin dashboard
# ------------------------------------------------------------

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()

    total_customers = (
        User.query
        .filter_by(role="customer")
        .count()
    )

    total_tailors = Tailor.query.count()
    total_orders = Order.query.count()

    completed_orders = (
        Order.query
        .filter_by(status="delivered")
        .all()
    )

    total_volume = sum(
        float(order.quotation or 0)
        for order in completed_orders
        if order.quotation is not None
    )

    pending_orders = (
        Order.query
        .filter_by(status="pending")
        .count()
    )

    in_progress_statuses = [
        "confirmed",
        "cutting",
        "stitching",
        "alteration",
        "quality_check",
    ]

    in_progress = (
        Order.query
        .filter(
            db.or_(
                Order.status == "confirmed",
                Order.status == "cutting",
                Order.status == "stitching",
                Order.status == "alteration",
                Order.status == "quality_check",
            )
        )
        .count()
    )

    recent_orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .limit(8)
        .all()
    )

    recent_users = (
        User.query
        .order_by(User.created_at.desc())
        .limit(5)
        .all()
    )

    verified_tailors = (
        Tailor.query
        .filter_by(is_verified=True)
        .count()
    )

    unverified_tailors = (
        Tailor.query
        .filter_by(is_verified=False)
        .count()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_customers=total_customers,
        total_tailors=total_tailors,
        total_orders=total_orders,
        total_volume=total_volume,
        pending_orders=pending_orders,
        in_progress=in_progress,
        verified_tailors=verified_tailors,
        unverified_tailors=unverified_tailors,
        recent_orders=recent_orders,
        recent_users=recent_users,
    )


# ------------------------------------------------------------
# Users
# ------------------------------------------------------------

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    role_filter = request.args.get(
        "role",
        "all",
    ).strip().lower()

    allowed_roles = {
        "all",
        "customer",
        "tailor",
        "admin",
    }

    if role_filter not in allowed_roles:
        role_filter = "all"

    query = User.query

    if role_filter != "all":
        query = query.filter_by(
            role=role_filter
        )

    user_list = (
        query
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/users.html",
        users=user_list,
        role_filter=role_filter,
    )


@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)

    return render_template(
        "admin/user_details.html",
        user=user,
    )


@admin_bp.route(
    "/users/<int:user_id>/toggle_status",
    methods=["POST"],
)
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent an admin from accidentally disabling
    # their own currently logged-in account.
    if user.id == current_user.id:
        flash(
            "You cannot deactivate your own admin account.",
            "warning",
        )
        return redirect(
            url_for("admin.users")
        )

    user.is_active = not user.is_active

    db.session.commit()

    status_label = (
        "activated"
        if user.is_active
        else "deactivated"
    )

    flash(
        f"User '{user.name}' has been "
        f"{status_label}.",
        "info",
    )

    return redirect(
        url_for("admin.users")
    )


# ------------------------------------------------------------
# Tailors
# ------------------------------------------------------------

@admin_bp.route("/tailors")
@login_required
@admin_required
def tailors():
    verification_filter = request.args.get(
        "verification",
        "all",
    ).strip().lower()

    query = Tailor.query

    if verification_filter == "verified":
        query = query.filter_by(
            is_verified=True
        )

    elif verification_filter == "unverified":
        query = query.filter_by(
            is_verified=False
        )

    else:
        verification_filter = "all"

    tailor_list = (
        query
        .order_by(Tailor.created_at.desc())
        .all()
    )

    return render_template(
        "admin/tailors.html",
        tailors=tailor_list,
        verification_filter=verification_filter,
    )


@admin_bp.route(
    "/tailors/<int:tailor_id>"
)
@login_required
@admin_required
def tailor_details(tailor_id):
    tailor = Tailor.query.get_or_404(
        tailor_id
    )

    orders = (
        Order.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    reviews = (
        Review.query
        .filter_by(tailor_id=tailor.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "admin/tailor_details.html",
        tailor=tailor,
        orders=orders,
        reviews=reviews,
    )


@admin_bp.route(
    "/tailors/<int:tailor_id>/toggle_verify",
    methods=["POST"],
)
@login_required
@admin_required
def toggle_verify_tailor(tailor_id):
    tailor = Tailor.query.get_or_404(
        tailor_id
    )

    tailor.is_verified = not tailor.is_verified

    db.session.commit()

    status_label = (
        "verified"
        if tailor.is_verified
        else "unverified"
    )

    flash(
        f"Tailor '{tailor.shop_name}' is now "
        f"{status_label}.",
        "success",
    )

    return redirect(
        url_for(
            "admin.tailor_details",
            tailor_id=tailor.id,
        )
    )


@admin_bp.route(
    "/tailors/<int:tailor_id>/toggle_status",
    methods=["POST"],
)
@login_required
@admin_required
def toggle_tailor_status(tailor_id):
    tailor = Tailor.query.get_or_404(
        tailor_id
    )

    tailor.is_active = not tailor.is_active

    db.session.commit()

    status_label = (
        "activated"
        if tailor.is_active
        else "deactivated"
    )

    flash(
        f"Tailor '{tailor.shop_name}' has been "
        f"{status_label}.",
        "info",
    )

    return redirect(
        url_for(
            "admin.tailor_details",
            tailor_id=tailor.id,
        )
    )


# ------------------------------------------------------------
# Orders
# ------------------------------------------------------------

@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    status_filter = request.args.get(
        "status",
        "all",
    ).strip().lower()

    query = Order.query

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
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template(
        "admin/orders.html",
        orders=orders_list,
        status_filter=status_filter,
        stages=Order.STATUS_FLOW,
        status_labels=Order.STATUS_LABELS,
    )


@admin_bp.route(
    "/orders/<int:order_id>"
)
@login_required
@admin_required
def order_details(order_id):
    order = Order.query.get_or_404(
        order_id
    )

    return render_template(
        "admin/order_details.html",
        order=order,
        stages=Order.STATUS_FLOW,
        status_labels=Order.STATUS_LABELS,
    )


# ------------------------------------------------------------
# Reviews
# ------------------------------------------------------------

@admin_bp.route("/reviews")
@login_required
@admin_required
def reviews():
    reviews_list = (
        Review.query
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "admin/reviews.html",
        reviews=reviews_list,
    )


@admin_bp.route(
    "/reviews/<int:review_id>/delete",
    methods=["POST"],
)
@login_required
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(
        review_id
    )

    tailor = Tailor.query.get(
        review.tailor_id
    )

    db.session.delete(review)

    # Recalculate the aggregate rating ourselves
    # because the rebuilt Tailor model does not expose
    # the old recalculate_rating() method.
    if tailor:
        remaining_reviews = (
            Review.query
            .filter(
                Review.tailor_id == tailor.id,
                Review.id != review.id,
            )
            .all()
        )

        if remaining_reviews:
            total_rating = sum(
                int(item.rating or 0)
                for item in remaining_reviews
            )

            tailor.total_reviews = len(
                remaining_reviews
            )

            tailor.rating = round(
                total_rating
                / len(remaining_reviews),
                2,
            )
        else:
            tailor.total_reviews = 0
            tailor.rating = 0

    db.session.commit()

    flash(
        "Review deleted successfully.",
        "info",
    )

    return redirect(
        url_for("admin.reviews")
    )