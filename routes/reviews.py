from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.review import Review
from models.order import Order
from models.tailor import Tailor
from utils.decorators import customer_required

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/')
def list_reviews():
    tailor_id = request.args.get('tailor_id', type=int)
    query = Review.query
    tailor = None
    if tailor_id:
        tailor = Tailor.query.get(tailor_id)
        query = query.filter_by(tailor_id=tailor_id)

    reviews = query.order_by(Review.created_at.desc()).all()
    return render_template('customer/reviews.html', reviews=reviews, tailor=tailor)


@reviews_bp.route('/submit/<int:order_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def submit_review(order_id):
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()

    # Can only review delivered/completed orders
    if order.status != 'delivered':
        flash('You can only review an order once it has been completed and delivered.', 'warning')
        return redirect(url_for('orders.order_details', order_id=order.id))

    existing_review = Review.query.filter_by(order_id=order.id).first()
    if existing_review:
        flash('You have already submitted a review for this order.', 'info')
        return redirect(url_for('orders.order_details', order_id=order.id))

    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating', 5))
            if rating < 1 or rating > 5:
                rating = 5
        except (ValueError, TypeError):
            rating = 5

        comment = request.form.get('comment', '').strip()

        review = Review(
            customer_id=current_user.id,
            tailor_id=order.tailor_id,
            order_id=order.id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()

        # Recalculate tailor rating and total_reviews
        order.tailor.recalculate_rating()

        flash('Thank you! Your review and rating have been posted.', 'success')
        return redirect(url_for('orders.order_details', order_id=order.id))

    return render_template('customer/reviews.html', order=order, tailor=order.tailor, is_submit_mode=True)
