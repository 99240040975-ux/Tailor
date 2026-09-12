from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.order import Order
from models.tailor import Tailor
from models.measurement import Measurement
from models.user import User
from models.message import Message
from utils.file_upload import save_uploaded_file
from utils.helpers import match_tailors_for_request

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/')
@login_required
def list_orders():
    if current_user.is_tailor:
        return redirect(url_for('tailor.orders'))

    status_filter = request.args.get('status', 'all')
    query = Order.query.filter_by(customer_id=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('customer/orders.html', orders=orders, status_filter=status_filter)


@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    if not current_user.is_customer:
        flash('Only customers can place tailoring orders.', 'warning')
        return redirect(url_for('index'))

    tailor_id = request.args.get('tailor_id', type=int)
    selected_tailor = Tailor.query.get(tailor_id) if tailor_id else None

    # Customer's saved measurement profiles
    measurements = Measurement.query.filter_by(customer_id=current_user.id).order_by(Measurement.created_at.desc()).all()

    # Intelligent match recommendations if not already picked
    matched_tailors = match_tailors_for_request(
        clothing_type=request.args.get('clothing_type'),
        service_type=request.args.get('service_type')
    )

    if request.method == 'POST':
        target_tailor_id = request.form.get('tailor_id', type=int)
        measurement_id = request.form.get('measurement_id', type=int)
        service_type = request.form.get('service_type', 'custom')
        clothing_type = request.form.get('clothing_type', '').strip()
        description = request.form.get('description', '').strip()
        delivery_method = request.form.get('delivery_method', 'pickup')
        delivery_address = request.form.get('delivery_address', '').strip()
        expected_date_str = request.form.get('expected_date', '').strip()

        if not target_tailor_id:
            flash('Please select a tailor for this order.', 'danger')
            return redirect(url_for('orders.create_order'))

        if not description:
            flash('Please provide details or requirements for your order.', 'danger')
            return redirect(url_for('orders.create_order', tailor_id=target_tailor_id))

        # Handle reference image upload
        ref_image = None
        if 'reference_image' in request.files:
            ref_image = save_uploaded_file(request.files['reference_image'], folder_name='reference')

        expected_date = None
        if expected_date_str:
            try:
                expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        new_order = Order(
            customer_id=current_user.id,
            tailor_id=target_tailor_id,
            measurement_id=measurement_id if measurement_id else None,
            service_type=service_type,
            clothing_type=clothing_type or 'Custom Garment',
            description=description,
            reference_image=ref_image,
            status='pending',
            delivery_method=delivery_method,
            delivery_address=delivery_address if delivery_method == 'delivery' else None,
            expected_date=expected_date
        )

        db.session.add(new_order)
        db.session.flush()

        # Send initial automated message/notification in order thread
        tailor = Tailor.query.get(target_tailor_id)
        if tailor:
            init_msg = Message(
                sender_id=current_user.id,
                receiver_id=tailor.user_id,
                order_id=new_order.id,
                message=f"Hello! I placed Order #{new_order.id} for {new_order.clothing_type} ({new_order.service_type}). Looking forward to your quotation."
            )
            db.session.add(init_msg)

        db.session.commit()
        flash(f'Order #{new_order.id} submitted successfully! The tailor will review and send a quotation.', 'success')
        return redirect(url_for('orders.order_details', order_id=new_order.id))

    all_tailors = Tailor.query.filter_by(availability=True).all()

    return render_template(
        'customer/create_order.html',
        selected_tailor=selected_tailor,
        all_tailors=all_tailors,
        measurements=measurements,
        matched_tailors=matched_tailors[:4]
    )


@orders_bp.route('/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)

    # Permission check: must be customer who placed it, the tailor assigned, or admin
    if current_user.is_customer and order.customer_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('orders.list_orders'))

    if current_user.is_tailor and (not current_user.tailor_profile or order.tailor_id != current_user.tailor_profile.id):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('tailor.orders'))

    if current_user.is_tailor:
        return redirect(url_for('tailor.order_details', order_id=order.id))

    return render_template('customer/order_details.html', order=order)


@orders_bp.route('/<int:order_id>/quotation', methods=['POST'])
@login_required
def submit_quotation(order_id):
    order = Order.query.get_or_404(order_id)
    tailor = current_user.tailor_profile

    if not tailor or order.tailor_id != tailor.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('tailor.orders'))

    try:
        quotation_amount = float(request.form.get('quotation', 0))
    except (ValueError, TypeError):
        flash('Please enter a valid quotation price.', 'danger')
        return redirect(url_for('tailor.order_details', order_id=order.id))

    notes = request.form.get('quotation_notes', '').strip()
    expected_date_str = request.form.get('expected_date', '').strip()

    order.quotation = quotation_amount
    order.quotation_notes = notes
    order.status = 'quoted'

    if expected_date_str:
        try:
            order.expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Send update message
    msg = Message(
        sender_id=current_user.id,
        receiver_id=order.customer_id,
        order_id=order.id,
        message=f"I have provided a quotation of ₹{quotation_amount:,.2f} for Order #{order.id}. Note: {notes}"
    )
    db.session.add(msg)
    db.session.commit()

    flash(f'Quotation of ₹{quotation_amount:,.2f} sent to customer.', 'success')
    return redirect(url_for('tailor.order_details', order_id=order.id))


@orders_bp.route('/<int:order_id>/accept_quote', methods=['POST'])
@login_required
def accept_quotation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('orders.list_orders'))

    order.status = 'confirmed'

    msg = Message(
        sender_id=current_user.id,
        receiver_id=order.tailor.user_id,
        order_id=order.id,
        message=f"Great! I have accepted the quotation of ₹{order.quotation:,.2f}. Please proceed with production."
    )
    db.session.add(msg)
    db.session.commit()

    flash('Quotation accepted! The tailor will now verify measurements and start cutting/stitching.', 'success')
    return redirect(url_for('orders.order_details', order_id=order.id))


@orders_bp.route('/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    tailor = current_user.tailor_profile

    if not current_user.is_admin and (not tailor or order.tailor_id != tailor.id):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('index'))

    new_status = request.form.get('status')
    valid_statuses = [s[0] for s in Order.STATUS_STAGES]

    if new_status in valid_statuses:
        order.status = new_status

        # Send update notification message to customer
        status_name = dict(Order.STATUS_STAGES).get(new_status, new_status)
        msg = Message(
            sender_id=current_user.id,
            receiver_id=order.customer_id,
            order_id=order.id,
            message=f"Order #{order.id} status updated to: {status_name}"
        )
        db.session.add(msg)
        db.session.commit()
        flash(f'Order #{order.id} status updated to {status_name}.', 'success')
    else:
        flash('Invalid status stage.', 'danger')

    if current_user.is_admin:
        return redirect(url_for('admin.order_details', order_id=order.id))
    return redirect(url_for('tailor.order_details', order_id=order.id))


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id and (not current_user.is_tailor or order.tailor_id != current_user.tailor_profile.id):
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('orders.list_orders'))

    order.status = 'cancelled'
    db.session.commit()
    flash('Order has been cancelled.', 'info')
    return redirect(url_for('orders.order_details', order_id=order.id))
