from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.tailor import Tailor
from models.order import Order
from models.review import Review
from models.message import Message
from models.user import User
from utils.decorators import tailor_required
from utils.file_upload import save_uploaded_file

tailor_bp = Blueprint('tailor', __name__)


@tailor_bp.route('/dashboard')
@login_required
@tailor_required
def dashboard():
    tailor = current_user.tailor_profile
    if not tailor:
        flash('Please complete your tailor profile.', 'warning')
        return redirect(url_for('tailor.edit_profile'))

    orders = Order.query.filter_by(tailor_id=tailor.id).order_by(Order.created_at.desc()).all()

    pending_count = sum(1 for o in orders if o.status == 'pending')
    active_count = sum(1 for o in orders if o.status in ['confirmed', 'cutting', 'stitching', 'alteration', 'quality_check'])
    ready_count = sum(1 for o in orders if o.status == 'ready')
    completed_count = sum(1 for o in orders if o.status == 'delivered')

    total_revenue = sum(o.quotation for o in orders if o.status == 'delivered' and o.quotation)

    recent_orders = orders[:6]
    recent_reviews = Review.query.filter_by(tailor_id=tailor.id).order_by(Review.created_at.desc()).limit(4).all()

    return render_template(
        'tailor/dashboard.html',
        tailor=tailor,
        pending_count=pending_count,
        active_count=active_count,
        ready_count=ready_count,
        completed_count=completed_count,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        recent_reviews=recent_reviews
    )


@tailor_bp.route('/profile')
@login_required
@tailor_required
def profile():
    tailor = current_user.tailor_profile
    if not tailor:
        return redirect(url_for('tailor.edit_profile'))
    reviews = Review.query.filter_by(tailor_id=tailor.id).order_by(Review.created_at.desc()).all()
    return render_template('tailor/profile.html', tailor=tailor, reviews=reviews)


@tailor_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@tailor_required
def edit_profile():
    tailor = current_user.tailor_profile
    if not tailor:
        tailor = Tailor(user_id=current_user.id, shop_name=f"{current_user.name}'s Tailoring")
        db.session.add(tailor)
        db.session.commit()

    if request.method == 'POST':
        tailor.shop_name = request.form.get('shop_name', '').strip() or tailor.shop_name
        tailor.specialization = request.form.get('specialization', '').strip()
        tailor.city = request.form.get('city', '').strip()
        tailor.address = request.form.get('address', '').strip()
        tailor.description = request.form.get('description', '').strip()
        tailor.price_range = request.form.get('price_range', '').strip()

        try:
            tailor.experience = int(request.form.get('experience', 0))
        except ValueError:
            pass

        tailor.availability = bool(request.form.get('availability'))

        if 'profile_pic' in request.files:
            pic_path = save_uploaded_file(request.files['profile_pic'], folder_name='profile')
            if pic_path:
                current_user.profile_pic = pic_path

        db.session.commit()
        flash('Studio profile updated successfully!', 'success')
        return redirect(url_for('tailor.profile'))

    return render_template('tailor/edit_profile.html', tailor=tailor)


@tailor_bp.route('/orders')
@login_required
@tailor_required
def orders():
    tailor = current_user.tailor_profile
    status_filter = request.args.get('status', 'all')

    query = Order.query.filter_by(tailor_id=tailor.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    orders_list = query.order_by(Order.updated_at.desc()).all()

    return render_template(
        'tailor/orders.html',
        orders=orders_list,
        status_filter=status_filter,
        stages=Order.STATUS_STAGES
    )


@tailor_bp.route('/orders/<int:order_id>')
@login_required
@tailor_required
def order_details(order_id):
    tailor = current_user.tailor_profile
    order = Order.query.filter_by(id=order_id, tailor_id=tailor.id).first_or_404()
    return render_template('tailor/order_details.html', order=order, stages=Order.STATUS_STAGES)


@tailor_bp.route('/quotations')
@login_required
@tailor_required
def quotations():
    tailor = current_user.tailor_profile
    pending_quotes = Order.query.filter_by(tailor_id=tailor.id, status='pending').all()
    quoted_orders = Order.query.filter_by(tailor_id=tailor.id, status='quoted').all()

    return render_template(
        'tailor/quotations.html',
        pending_quotes=pending_quotes,
        quoted_orders=quoted_orders
    )


@tailor_bp.route('/messages')
@login_required
@tailor_required
def messages():
    return redirect(url_for('customer.messages'))


@tailor_bp.route('/reviews')
@login_required
@tailor_required
def reviews():
    tailor = current_user.tailor_profile
    reviews_list = Review.query.filter_by(tailor_id=tailor.id).order_by(Review.created_at.desc()).all()
    return render_template('tailor/reviews.html', tailor=tailor, reviews=reviews_list)
