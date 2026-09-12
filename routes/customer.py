from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.tailor import Tailor
from models.order import Order
from models.measurement import Measurement
from models.message import Message
from models.review import Review
from utils.decorators import customer_required
from utils.file_upload import save_uploaded_file
from utils.helpers import match_tailors_for_request

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    active_orders = Order.query.filter(
        Order.customer_id == current_user.id,
        Order.status.notin_(['delivered', 'cancelled'])
    ).order_by(Order.updated_at.desc()).all()

    completed_orders = Order.query.filter_by(
        customer_id=current_user.id,
        status='delivered'
    ).count()

    measurement_count = Measurement.query.filter_by(customer_id=current_user.id).count()

    # Recommended tailors based on highest ratings & availability
    top_tailors = Tailor.query.filter_by(availability=True).order_by(
        Tailor.rating.desc(), Tailor.total_reviews.desc()
    ).limit(4).all()

    return render_template(
        'customer/dashboard.html',
        active_orders=active_orders,
        completed_orders=completed_orders,
        measurement_count=measurement_count,
        top_tailors=top_tailors
    )


@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@customer_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()

        if name:
            current_user.name = name
        current_user.phone = phone

        if 'profile_pic' in request.files:
            pic_path = save_uploaded_file(request.files['profile_pic'], folder_name='profile')
            if pic_path:
                current_user.profile_pic = pic_path

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer.profile'))

    return render_template('customer/profile.html')


@customer_bp.route('/tailors')
def tailors():
    """Discover local tailors with search and filters."""
    search_q = request.args.get('q', '').strip()
    city = request.args.get('city', '').strip()
    specialization = request.args.get('specialization', '').strip()
    min_rating = request.args.get('min_rating', type=float)
    available_only = request.args.get('available') == '1'
    sort = request.args.get('sort', 'rating_desc')

    query = Tailor.query

    if search_q:
        query = query.filter(
            (Tailor.shop_name.ilike(f'%{search_q}%')) |
            (Tailor.specialization.ilike(f'%{search_q}%')) |
            (Tailor.description.ilike(f'%{search_q}%'))
        )
    if city:
        query = query.filter(Tailor.city.ilike(f'%{city}%'))
    if specialization:
        query = query.filter(Tailor.specialization.ilike(f'%{specialization}%'))
    if min_rating:
        query = query.filter(Tailor.rating >= min_rating)
    if available_only:
        query = query.filter(Tailor.availability == True)

    # Sorting
    if sort == 'rating_desc':
        query = query.order_by(Tailor.rating.desc(), Tailor.total_reviews.desc())
    elif sort == 'experience_desc':
        query = query.order_by(Tailor.experience.desc())
    elif sort == 'reviews_desc':
        query = query.order_by(Tailor.total_reviews.desc())
    else:
        query = query.order_by(Tailor.id.desc())

    tailors_list = query.all()
    cities = [c[0] for c in db.session.query(Tailor.city).distinct().all() if c[0]]

    return render_template(
        'customer/tailors.html',
        tailors=tailors_list,
        cities=cities,
        search_q=search_q,
        selected_city=city,
        selected_spec=specialization,
        selected_sort=sort,
        available_only=available_only
    )


@customer_bp.route('/tailors/<int:tailor_id>')
def tailor_details(tailor_id):
    tailor = Tailor.query.get_or_404(tailor_id)
    reviews = Review.query.filter_by(tailor_id=tailor.id).order_by(Review.created_at.desc()).all()
    return render_template('customer/tailor_details.html', tailor=tailor, reviews=reviews)


@customer_bp.route('/messages', methods=['GET'])
@login_required
def messages():
    order_id = request.args.get('order_id', type=int)
    recipient_id = request.args.get('user_id', type=int)

    # All conversations involving current_user
    sent = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    contact_ids = set([r[0] for r in sent.union(received).all()])

    contacts = User.query.filter(User.id.in_(contact_ids)).all() if contact_ids else []

    active_contact = None
    chat_messages = []
    active_order = None

    if order_id:
        active_order = Order.query.get(order_id)
        if active_order:
            if current_user.is_customer and active_order.tailor:
                active_contact = active_order.tailor.user
            elif current_user.is_tailor:
                active_contact = active_order.customer

    if not active_contact and recipient_id:
        active_contact = User.query.get(recipient_id)

    if not active_contact and contacts:
        active_contact = contacts[0]

    if active_contact:
        query = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == active_contact.id)) |
            ((Message.sender_id == active_contact.id) & (Message.receiver_id == current_user.id))
        )
        if order_id:
            query = query.filter((Message.order_id == order_id) | (Message.order_id == None))

        chat_messages = query.order_by(Message.created_at.asc()).all()

        # Mark received messages as read
        Message.query.filter_by(
            sender_id=active_contact.id,
            receiver_id=current_user.id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()

    return render_template(
        'customer/messages.html',
        contacts=contacts,
        active_contact=active_contact,
        active_order=active_order,
        chat_messages=chat_messages
    )


@customer_bp.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    receiver_id = request.form.get('receiver_id', type=int)
    order_id = request.form.get('order_id', type=int)
    message_text = request.form.get('message', '').strip()

    if not receiver_id or not message_text:
        flash('Message text cannot be empty.', 'danger')
        return redirect(request.referrer or url_for('customer.messages'))

    msg = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        order_id=order_id if order_id else None,
        message=message_text
    )
    db.session.add(msg)
    db.session.commit()

    flash('Message sent!', 'success')
    return redirect(url_for('customer.messages', user_id=receiver_id, order_id=order_id))
