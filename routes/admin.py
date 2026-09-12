from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.tailor import Tailor
from models.order import Order
from models.review import Review
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_tailors = Tailor.query.count()
    total_orders = Order.query.count()

    completed_orders = Order.query.filter_by(status='delivered').all()
    total_volume = sum(o.quotation for o in completed_orders if o.quotation)

    pending_orders = Order.query.filter_by(status='pending').count()
    in_progress = Order.query.filter(Order.status.in_(['confirmed', 'cutting', 'stitching', 'alteration'])).count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_customers=total_customers,
        total_tailors=total_tailors,
        total_orders=total_orders,
        total_volume=total_volume,
        pending_orders=pending_orders,
        in_progress=in_progress,
        recent_orders=recent_orders,
        recent_users=recent_users
    )


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role_filter = request.args.get('role', 'all')
    query = User.query

    if role_filter != 'all':
        query = query.filter_by(role=role_filter)

    user_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=user_list, role_filter=role_filter)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_details.html', user=user)


@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_account = not user.is_active_account
    db.session.commit()
    status_label = "activated" if user.is_active_account else "deactivated"
    flash(f"User '{user.name}' has been {status_label}.", 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/tailors')
@login_required
@admin_required
def tailors():
    tailor_list = Tailor.query.order_by(Tailor.id.desc()).all()
    return render_template('admin/tailors.html', tailors=tailor_list)


@admin_bp.route('/tailors/<int:tailor_id>')
@login_required
@admin_required
def tailor_details(tailor_id):
    tailor = Tailor.query.get_or_404(tailor_id)
    orders = Order.query.filter_by(tailor_id=tailor.id).order_by(Order.created_at.desc()).all()
    reviews = Review.query.filter_by(tailor_id=tailor.id).order_by(Review.created_at.desc()).all()
    return render_template('admin/tailor_details.html', tailor=tailor, orders=orders, reviews=reviews)


@admin_bp.route('/tailors/<int:tailor_id>/toggle_verify', methods=['POST'])
@login_required
@admin_required
def toggle_verify_tailor(tailor_id):
    tailor = Tailor.query.get_or_404(tailor_id)
    tailor.is_verified = not tailor.is_verified
    db.session.commit()
    flash(f"Tailor '{tailor.shop_name}' verification set to {tailor.is_verified}.", 'success')
    return redirect(url_for('admin.tailor_details', tailor_id=tailor.id))


@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    status_filter = request.args.get('status', 'all')
    query = Order.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    orders_list = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders_list, status_filter=status_filter, stages=Order.STATUS_STAGES)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order, stages=Order.STATUS_STAGES)


@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    reviews_list = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews_list)


@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    tailor = review.tailor
    db.session.delete(review)
    db.session.commit()
    if tailor:
        tailor.recalculate_rating()
    flash('Review deleted successfully.', 'info')
    return redirect(url_for('admin.reviews'))
