from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.measurement import Measurement
from utils.decorators import customer_required
from utils.validators import validate_measurement_value

measurements_bp = Blueprint('measurements', __name__)


@measurements_bp.route('/')
@login_required
@customer_required
def list_measurements():
    profiles = Measurement.query.filter_by(customer_id=current_user.id).order_by(Measurement.created_at.desc()).all()
    return render_template('customer/measurements.html', profiles=profiles)


@measurements_bp.route('/add', methods=['GET', 'POST'])
@login_required
@customer_required
def add_measurement():
    if request.method == 'POST':
        profile_name = request.form.get('profile_name', '').strip()
        unit = request.form.get('unit', 'inches')
        notes = request.form.get('notes', '').strip()

        if not profile_name:
            flash('Profile name is required (e.g., "Formal Suit", "Daily Wear").', 'danger')
            return render_template('customer/add_measurement.html', **request.form)

        fields = ['chest', 'waist', 'hip', 'shoulder', 'sleeve', 'neck', 'inseam', 'height']
        meas_vals = {}

        for f in fields:
            val = request.form.get(f, '').strip()
            if val:
                valid, err = validate_measurement_value(f, val, unit)
                if not valid:
                    flash(err, 'danger')
                    return render_template('customer/add_measurement.html', **request.form)
                try:
                    meas_vals[f] = float(val)
                except ValueError:
                    meas_vals[f] = None
            else:
                meas_vals[f] = None

        new_meas = Measurement(
            customer_id=current_user.id,
            profile_name=profile_name,
            unit=unit,
            notes=notes,
            **meas_vals
        )
        db.session.add(new_meas)
        db.session.commit()

        flash(f'Measurement profile "{profile_name}" saved successfully! You can reuse it for any order.', 'success')
        return redirect(url_for('measurements.list_measurements'))

    return render_template('customer/add_measurement.html')


@measurements_bp.route('/<int:meas_id>/edit', methods=['GET', 'POST'])
@login_required
@customer_required
def edit_measurement(meas_id):
    meas = Measurement.query.filter_by(id=meas_id, customer_id=current_user.id).first_or_404()

    if request.method == 'POST':
        profile_name = request.form.get('profile_name', '').strip()
        unit = request.form.get('unit', 'inches')
        notes = request.form.get('notes', '').strip()

        if not profile_name:
            flash('Profile name is required.', 'danger')
            return render_template('customer/edit_measurement.html', measurement=meas)

        fields = ['chest', 'waist', 'hip', 'shoulder', 'sleeve', 'neck', 'inseam', 'height']
        for f in fields:
            val = request.form.get(f, '').strip()
            if val:
                valid, err = validate_measurement_value(f, val, unit)
                if not valid:
                    flash(err, 'danger')
                    return render_template('customer/edit_measurement.html', measurement=meas)
                setattr(meas, f, float(val))
            else:
                setattr(meas, f, None)

        meas.profile_name = profile_name
        meas.unit = unit
        meas.notes = notes

        db.session.commit()
        flash(f'Measurement profile "{profile_name}" updated successfully!', 'success')
        return redirect(url_for('measurements.list_measurements'))

    return render_template('customer/edit_measurement.html', measurement=meas)


@measurements_bp.route('/<int:meas_id>/delete', methods=['POST'])
@login_required
@customer_required
def delete_measurement(meas_id):
    meas = Measurement.query.filter_by(id=meas_id, customer_id=current_user.id).first_or_404()
    db.session.delete(meas)
    db.session.commit()
    flash('Measurement profile deleted.', 'info')
    return redirect(url_for('measurements.list_measurements'))


@measurements_bp.route('/<int:meas_id>/json')
@login_required
def get_measurement_json(meas_id):
    meas = Measurement.query.filter_by(id=meas_id).first_or_404()
    # Check permissions
    if meas.customer_id != current_user.id and not current_user.is_tailor and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(meas.to_dict())
