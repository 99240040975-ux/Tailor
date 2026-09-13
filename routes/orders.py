from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.measurement import Measurement
from models.message import Message
from models.order import Order
from models.tailor import Tailor
from utils.file_upload import save_uploaded_file
from utils.helpers import match_tailors_for_request


orders_bp = Blueprint("orders", __name__)


def _customer_can_access(order):
    return current_user.is_customer and order.customer_id == current_user.id


def _tailor_can_access(order):
    tailor = current_user.tailor_profile
    return (
        current_user.is_tailor
        and tailor is not None
        and order.tailor_id == tailor.id
    )


def _parse_expected_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@orders_bp.route("/")
@login_required
def list_orders():
    if current_user.is_tailor:
        return redirect(url_for("tailor.orders"))

    if current_user.is_admin:
        return redirect(url_for("admin.orders"))

    status_filter = request.args.get("status", "all").strip().lower()

    query = Order.query.filter_by(customer_id=current_user.id)

    if status_filter != "all":
        if status_filter not in Order.STATUS_FLOW and status_filter != "cancelled":
            flash("Invalid order status filter.", "warning")
            status_filter = "all"
        else:
            query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()

    return render_template(
        "customer/orders.html",
        orders=orders,
        status_filter=status_filter,
        status_flow=Order.STATUS_FLOW,
        status_labels=Order.STATUS_LABELS,
    )


@orders_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_order():
    if not current_user.is_customer:
        flash("Only customers can place tailoring orders.", "warning")
        return redirect(url_for("index"))

    tailor_id = request.args.get("tailor_id", type=int)

    selected_tailor = None
    if tailor_id:
        selected_tailor = (
            Tailor.query
            .filter_by(id=tailor_id, is_active=True)
            .first()
        )

        if not selected_tailor:
            flash("The selected tailor is not available.", "warning")
            tailor_id = None

    measurements = (
        Measurement.query
        .filter_by(customer_id=current_user.id)
        .order_by(
            Measurement.is_default.desc(),
            Measurement.updated_at.desc(),
            Measurement.created_at.desc(),
        )
        .all()
    )

    matched_tailors = match_tailors_for_request(
        clothing_type=request.args.get("clothing_type"),
        service_type=request.args.get("service_type"),
    )

    if request.method == "POST":
        target_tailor_id = request.form.get("tailor_id", type=int)
        measurement_id = request.form.get("measurement_id", type=int)

        service_type = (
            request.form.get("service_type", "custom")
            .strip()
            .lower()
        )
        clothing_type = request.form.get("clothing_type", "").strip()
        description = request.form.get("description", "").strip()

        delivery_method = (
            request.form.get("delivery_method", "pickup")
            .strip()
            .lower()
        )
        delivery_address = request.form.get("delivery_address", "").strip()

        expected_date_str = request.form.get("expected_date", "").strip()

        if not target_tailor_id:
            flash("Please select a tailor for this order.", "danger")
            return redirect(url_for("orders.create_order"))

        target_tailor = (
            Tailor.query
            .filter_by(id=target_tailor_id, is_active=True)
            .first()
        )

        if not target_tailor:
            flash("The selected tailor is not available.", "danger")
            return redirect(url_for("orders.create_order"))

        if not description:
            flash(
                "Please provide details or requirements for your order.",
                "danger",
            )
            return redirect(
                url_for(
                    "orders.create_order",
                    tailor_id=target_tailor_id,
                )
            )

        if delivery_method not in {"pickup", "delivery"}:
            delivery_method = "pickup"

        selected_measurement = None

        if measurement_id:
            selected_measurement = (
                Measurement.query
                .filter_by(
                    id=measurement_id,
                    customer_id=current_user.id,
                )
                .first()
            )

            if not selected_measurement:
                flash(
                    "The selected measurement profile is invalid.",
                    "danger",
                )
                return redirect(
                    url_for(
                        "orders.create_order",
                        tailor_id=target_tailor_id,
                    )
                )

        expected_date = _parse_expected_date(expected_date_str)

        if expected_date_str and expected_date is None:
            flash(
                "Please enter a valid expected date.",
                "danger",
            )
            return redirect(
                url_for(
                    "orders.create_order",
                    tailor_id=target_tailor_id,
                )
            )

        reference_image = None

        uploaded_file = request.files.get("reference_image")

        if uploaded_file and uploaded_file.filename:
            try:
                reference_image = save_uploaded_file(
                    uploaded_file,
                    folder_name="reference",
                )
            except Exception:
                flash(
                    "The reference image could not be uploaded. "
                    "Please try again.",
                    "danger",
                )
                return redirect(
                    url_for(
                        "orders.create_order",
                        tailor_id=target_tailor_id,
                    )
                )

        new_order = Order(
            customer_id=current_user.id,
            tailor_id=target_tailor_id,
            measurement_id=(
                selected_measurement.id
                if selected_measurement
                else None
            ),
            service_type=service_type or "custom",
            clothing_type=clothing_type or "Custom Garment",
            description=description,
            reference_image=reference_image,
            quotation=None,
            quotation_notes=None,
            status="pending",
            delivery_method=delivery_method,
            delivery_address=(
                delivery_address
                if delivery_method == "delivery"
                else None
            ),
            expected_date=expected_date,
        )

        try:
            db.session.add(new_order)
            db.session.flush()

            initial_message = Message(
                sender_id=current_user.id,
                receiver_id=target_tailor.user_id,
                order_id=new_order.id,
                message=(
                    f"Hello! I placed Order #{new_order.id} for "
                    f"{new_order.clothing_type} "
                    f"({new_order.service_type}). "
                    "Looking forward to your quotation."
                ),
            )

            db.session.add(initial_message)
            db.session.commit()

        except Exception:
            db.session.rollback()
            flash(
                "We couldn't create your order right now. "
                "Please try again.",
                "danger",
            )
            return redirect(
                url_for(
                    "orders.create_order",
                    tailor_id=target_tailor_id,
                )
            )

        flash(
            f"Order #{new_order.id} submitted successfully! "
            "The tailor will review it and send a quotation.",
            "success",
        )

        return redirect(
            url_for(
                "orders.order_details",
                order_id=new_order.id,
            )
        )

    all_tailors = (
        Tailor.query
        .filter_by(is_active=True)
        .order_by(
            Tailor.is_verified.desc(),
            Tailor.rating.desc(),
            Tailor.shop_name.asc(),
        )
        .all()
    )

    return render_template(
        "customer/create_order.html",
        selected_tailor=selected_tailor,
        all_tailors=all_tailors,
        measurements=measurements,
        matched_tailors=matched_tailors[:4],
        status_flow=Order.STATUS_FLOW,
        status_labels=Order.STATUS_LABELS,
    )


@orders_bp.route("/<int:order_id>")
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.is_admin:
        return redirect(
            url_for(
                "admin.order_details",
                order_id=order.id,
            )
        )

    if current_user.is_tailor:
        if not _tailor_can_access(order):
            flash("Unauthorized access.", "danger")
            return redirect(url_for("tailor.orders"))

        return redirect(
            url_for(
                "tailor.order_details",
                order_id=order.id,
            )
        )

    if not _customer_can_access(order):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("orders.list_orders"))

    return render_template(
        "customer/order_details.html",
        order=order,
        status_flow=Order.STATUS_FLOW,
        status_labels=Order.STATUS_LABELS,
    )


@orders_bp.route("/<int:order_id>/quotation", methods=["POST"])
@login_required
def submit_quotation(order_id):
    order = Order.query.get_or_404(order_id)

    if not current_user.is_tailor:
        flash("Only tailors can submit quotations.", "warning")
        return redirect(url_for("index"))

    tailor = current_user.tailor_profile

    if not tailor or order.tailor_id != tailor.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("tailor.orders"))

    if order.status != "pending":
        flash(
            "A quotation can only be submitted for a pending order.",
            "warning",
        )
        return redirect(
            url_for(
                "tailor.order_details",
                order_id=order.id,
            )
        )

    quotation_raw = request.form.get("quotation", "").strip()

    try:
        quotation_amount = float(quotation_raw)
    except (ValueError, TypeError):
        quotation_amount = 0

    if quotation_amount <= 0:
        flash(
            "Please enter a valid quotation price greater than zero.",
            "danger",
        )
        return redirect(
            url_for(
                "tailor.order_details",
                order_id=order.id,
            )
        )

    notes = request.form.get("quotation_notes", "").strip()

    expected_date_str = request.form.get(
        "expected_date",
        "",
    ).strip()

    if expected_date_str:
        parsed_date = _parse_expected_date(expected_date_str)

        if parsed_date is None:
            flash(
                "Please enter a valid expected delivery date.",
                "danger",
            )
            return redirect(
                url_for(
                    "tailor.order_details",
                    order_id=order.id,
                )
            )

        order.expected_date = parsed_date

    order.quotation = quotation_amount
    order.quotation_notes = notes
    order.status = "quoted"

    message_text = (
        f"I have provided a quotation of "
        f"₹{quotation_amount:,.2f} for Order #{order.id}."
    )

    if notes:
        message_text += f" Note: {notes}"

    message = Message(
        sender_id=current_user.id,
        receiver_id=order.customer_id,
        order_id=order.id,
        message=message_text,
    )

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash(
            "The quotation could not be saved. Please try again.",
            "danger",
        )
        return redirect(
            url_for(
                "tailor.order_details",
                order_id=order.id,
            )
        )

    flash(
        f"Quotation of ₹{quotation_amount:,.2f} sent to customer.",
        "success",
    )

    return redirect(
        url_for(
            "tailor.order_details",
            order_id=order.id,
        )
    )


@orders_bp.route("/<int:order_id>/accept_quote", methods=["POST"])
@login_required
def accept_quotation(order_id):
    order = Order.query.get_or_404(order_id)

    if not _customer_can_access(order):
        flash("Unauthorized.", "danger")
        return redirect(url_for("orders.list_orders"))

    if order.status != "quoted":
        flash(
            "This order does not currently have a quotation to accept.",
            "warning",
        )
        return redirect(
            url_for(
                "orders.order_details",
                order_id=order.id,
            )
        )

    if order.quotation is None or order.quotation <= 0:
        flash(
            "This order does not have a valid quotation.",
            "warning",
        )
        return redirect(
            url_for(
                "orders.order_details",
                order_id=order.id,
            )
        )

    if not order.tailor or not order.tailor.user_id:
        flash(
            "The assigned tailor could not be found.",
            "danger",
        )
        return redirect(
            url_for(
                "orders.order_details",
                order_id=order.id,
            )
        )

    order.status = "confirmed"

    message = Message(
        sender_id=current_user.id,
        receiver_id=order.tailor.user_id,
        order_id=order.id,
        message=(
            f"Great! I have accepted the quotation of "
            f"₹{order.quotation:,.2f}. "
            "Please proceed with production."
        ),
    )

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash(
            "The quotation could not be accepted. Please try again.",
            "danger",
        )
        return redirect(
            url_for(
                "orders.order_details",
                order_id=order.id,
            )
        )

    flash(
        "Quotation accepted! The tailor can now begin production.",
        "success",
    )

    return redirect(
        url_for(
            "orders.order_details",
            order_id=order.id,
        )
    )


@orders_bp.route("/<int:order_id>/update_status", methods=["POST"])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.is_admin:
        allowed = True
    else:
        allowed = _tailor_can_access(order)

    if not allowed:
        flash("Unauthorized.", "danger")
        return redirect(url_for("index"))

    new_status = (
        request.form.get("status", "")
        .strip()
        .lower()
    )

    if new_status not in Order.STATUS_FLOW:
        flash("Invalid status stage.", "danger")
        return _status_redirect(order)

    current_status = order.status

    if current_user.is_tailor:
        if not order.can_move_to(new_status):
            flash(
                "Order status must move through the production stages "
                "in order.",
                "warning",
            )
            return _status_redirect(order)

    order.status = new_status

    status_name = Order.STATUS_LABELS.get(
        new_status,
        new_status.replace("_", " ").title(),
    )

    message = Message(
        sender_id=current_user.id,
        receiver_id=order.customer_id,
        order_id=order.id,
        message=(
            f"Order #{order.id} status updated to: "
            f"{status_name}"
        ),
    )

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash(
            "The order status could not be updated.",
            "danger",
        )
        return _status_redirect(order)

    if current_status != new_status:
        flash(
            f"Order #{order.id} status updated to {status_name}.",
            "success",
        )

    return _status_redirect(order)


@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    customer_allowed = _customer_can_access(order)
    tailor_allowed = _tailor_can_access(order)

    if not customer_allowed and not tailor_allowed:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("index"))

    if order.status in {"delivered", "cancelled"}:
        flash(
            "This order can no longer be cancelled.",
            "warning",
        )
        return _status_redirect(order)

    order.status = "cancelled"

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash(
            "The order could not be cancelled.",
            "danger",
        )
        return _status_redirect(order)

    flash("Order has been cancelled.", "info")

    return _status_redirect(order)


@orders_bp.route("/<int:order_id>/status", methods=["GET"])
@login_required
def order_status_api(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.is_admin:
        allowed = True
    elif current_user.is_customer:
        allowed = order.customer_id == current_user.id
    else:
        allowed = _tailor_can_access(order)

    if not allowed:
        return jsonify(
            {
                "success": False,
                "message": "Unauthorized access.",
            }
        ), 403

    return jsonify(
        {
            "success": True,
            "order": order.to_dict(),
        }
    )


def _status_redirect(order):
    if current_user.is_admin:
        return redirect(
            url_for(
                "admin.order_details",
                order_id=order.id,
            )
        )

    if current_user.is_tailor:
        return redirect(
            url_for(
                "tailor.order_details",
                order_id=order.id,
            )
        )

    return redirect(
        url_for(
            "orders.order_details",
            order_id=order.id,
        )
    )