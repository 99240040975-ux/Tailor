from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from models import db
from models.order import Order
from models.review import Review
from models.tailor import Tailor
from utils.decorators import customer_required


reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/create/<int:order_id>", methods=["POST"])
@login_required
@customer_required
def create_review(order_id):
    """Create a review for a delivered order."""

    order = db.session.get(Order, order_id)

    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.list_orders"))

    if order.customer_id != current_user.id:
        flash("You are not allowed to review this order.", "error")
        return redirect(url_for("orders.list_orders"))

    if order.status != "delivered":
        flash("You can review an order only after it has been delivered.", "error")
        return redirect(url_for("orders.order_details", order_id=order.id))

    existing_review = Review.query.filter_by(
        order_id=order.id
    ).first()

    if existing_review:
        flash("You have already reviewed this order.", "info")
        return redirect(url_for("orders.order_details", order_id=order.id))

    try:
        rating = int(request.form.get("rating", 0))
    except (TypeError, ValueError):
        rating = 0

    comment = request.form.get("comment", "").strip()

    if rating < 1 or rating > 5:
        flash("Please select a rating from 1 to 5.", "error")
        return redirect(url_for("orders.order_details", order_id=order.id))

    if len(comment) > 2000:
        flash("Review comment is too long.", "error")
        return redirect(url_for("orders.order_details", order_id=order.id))

    review = Review(
        customer_id=current_user.id,
        tailor_id=order.tailor_id,
        order_id=order.id,
        rating=rating,
        comment=comment or None,
    )

    try:
        db.session.add(review)
        db.session.flush()  # assign review.id and persist without commit

        tailor = db.session.get(Tailor, order.tailor_id)

        if tailor:
            from sqlalchemy import func
            result = db.session.query(
                func.count(Review.id),
                func.avg(Review.rating),
            ).filter(Review.tailor_id == tailor.id).one()

            tailor.total_reviews = result[0] or 0
            tailor.rating = round(float(result[1]), 2) if result[1] else 0.0

        db.session.commit()

        flash("Thank you! Your review has been submitted.", "success")

    except Exception:
        db.session.rollback()
        flash(
            "Could not submit your review. Please try again.",
            "error",
        )

    return redirect(url_for("orders.order_details", order_id=order.id))


@reviews_bp.route("/delete/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    """Delete a review. Customers can delete their own reviews; admins can delete any review."""

    review = db.session.get(Review, review_id)

    if not review:
        flash("Review not found.", "error")
        return redirect(url_for("index"))

    if not current_user.is_admin and review.customer_id != current_user.id:
        flash("You are not allowed to delete this review.", "error")
        return redirect(url_for("index"))

    tailor = db.session.get(Tailor, review.tailor_id)

    try:
        db.session.delete(review)
        db.session.flush()

        if tailor:
            remaining_reviews = Review.query.filter_by(
                tailor_id=tailor.id
            ).all()

            tailor.total_reviews = len(remaining_reviews)

            if remaining_reviews:
                tailor.rating = round(
                    sum(item.rating for item in remaining_reviews)
                    / len(remaining_reviews),
                    2,
                )
            else:
                tailor.rating = 0.0

        db.session.commit()

        flash("Review deleted successfully.", "success")

    except Exception:
        db.session.rollback()
        flash(
            "Could not delete the review. Please try again.",
            "error",
        )

    if current_user.is_admin:
        return redirect(url_for("admin.reviews"))

    return redirect(url_for("customer.dashboard"))


@reviews_bp.route("/<int:review_id>/rating", methods=["POST"])
@login_required
def update_rating(review_id):
    """Update a review rating."""

    review = db.session.get(Review, review_id)

    if not review:
        flash("Review not found.", "error")
        return redirect(url_for("index"))

    if review.customer_id != current_user.id and not current_user.is_admin:
        flash("You are not allowed to edit this review.", "error")
        return redirect(url_for("index"))

    try:
        rating = int(request.form.get("rating", 0))
    except (TypeError, ValueError):
        rating = 0

    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(
            url_for(
                "orders.order_details",
                order_id=review.order_id,
            )
        )

    review.rating = rating

    comment = request.form.get("comment")

    if comment is not None:
        comment = comment.strip()

        if len(comment) > 2000:
            flash("Review comment is too long.", "error")
            return redirect(
                url_for(
                    "orders.order_details",
                    order_id=review.order_id,
                )
            )

        review.comment = comment or None

    tailor = db.session.get(Tailor, review.tailor_id)

    try:
        if tailor:
            reviews = Review.query.filter(
                Review.tailor_id == tailor.id,
                Review.id != review.id,
            ).all()

            total_reviews = len(reviews) + 1
            total_rating = sum(
                item.rating for item in reviews
            ) + review.rating

            tailor.total_reviews = total_reviews
            tailor.rating = round(
                total_rating / total_reviews,
                2,
            )

        db.session.commit()

        flash("Review updated successfully.", "success")

    except Exception:
        db.session.rollback()
        flash(
            "Could not update the review. Please try again.",
            "error",
        )

    return redirect(
        url_for(
            "orders.order_details",
            order_id=review.order_id,
        )
    )