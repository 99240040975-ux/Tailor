from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from models import db
from models.measurement import Measurement
from utils.decorators import customer_required
from utils.validators import validate_measurement_value


measurements_bp = Blueprint(
    "measurements",
    __name__,
)


MEASUREMENT_FIELDS = [
    "chest",
    "waist",
    "hip",
    "shoulder",
    "sleeve",
    "neck",
    "inseam",
    "height",
]


def _parse_measurements(
    form,
    unit,
) -> tuple[dict[str, float | None], str | None]:
    """
    Validate and convert measurement form values.

    Returns:
        (values, error)
    """
    values: dict[str, float | None] = {}

    for field in MEASUREMENT_FIELDS:
        raw_value = form.get(
            field,
            "",
        ).strip()

        if not raw_value:
            values[field] = None
            continue

        valid, error = validate_measurement_value(
            field,
            raw_value,
            unit,
        )

        if not valid:
            return None, error

        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError):
            return None, (
                f"{field.title()} must be a valid number."
            )

        if numeric_value <= 0:
            return None, (
                f"{field.title()} must be greater than zero."
            )

        values[field] = numeric_value

    return values, None


def _set_default_profile(measurement):
    """
    Make one measurement profile the customer's default
    and clear the default flag from all other profiles.
    """
    Measurement.query.filter(
        Measurement.customer_id == measurement.customer_id,
        Measurement.id != measurement.id,
    ).update(
        {"is_default": False},
        synchronize_session=False,
    )

    measurement.is_default = True


# ------------------------------------------------------------
# Measurement profiles
# ------------------------------------------------------------

@measurements_bp.route("/")
@login_required
@customer_required
def list_measurements():
    profiles = (
        Measurement.query
        .filter_by(customer_id=current_user.id)
        .order_by(
            Measurement.is_default.desc(),
            Measurement.created_at.desc(),
        )
        .all()
    )

    return render_template(
        "customer/measurements.html",
        profiles=profiles,
    )


# ------------------------------------------------------------
# Add measurement profile
# ------------------------------------------------------------

@measurements_bp.route(
    "/add",
    methods=["GET", "POST"],
)
@login_required
@customer_required
def add_measurement():
    if request.method == "POST":
        profile_name = request.form.get(
            "profile_name",
            "",
        ).strip()

        unit = request.form.get(
            "unit",
            "inches",
        ).strip().lower()

        notes = request.form.get(
            "notes",
            "",
        ).strip()

        is_default = (
            request.form.get("is_default")
            in {"on", "true", "1", "yes"}
        )

        if not profile_name:
            flash(
                "Profile name is required "
                '(for example, "Formal Suit").',
                "danger",
            )

            return render_template(
                "customer/add_measurement.html",
                **request.form,
            )

        if unit not in {
            "inches",
            "inch",
            "cm",
            "centimeters",
        }:
            unit = "inches"

        measurement_values, error = (
            _parse_measurements(
                request.form,
                unit,
            )
        )

        if error:
            flash(error, "danger")

            return render_template(
                "customer/add_measurement.html",
                **request.form,
            )

        new_measurement = Measurement(
            customer_id=current_user.id,
            profile_name=profile_name,
            unit=unit,
            notes=notes or None,
            is_default=False,
            **measurement_values,
        )

        db.session.add(new_measurement)
        db.session.flush()

        existing_count = (
            Measurement.query
            .filter_by(
                customer_id=current_user.id,
            )
            .count()
        )

        # The first profile automatically becomes default.
        if is_default or existing_count == 1:
            _set_default_profile(
                new_measurement
            )

        db.session.commit()

        flash(
            f'Measurement profile "{profile_name}" '
            "saved successfully!",
            "success",
        )

        return redirect(
            url_for(
                "measurements.list_measurements"
            )
        )

    return render_template(
        "customer/add_measurement.html"
    )


# ------------------------------------------------------------
# Edit measurement profile
# ------------------------------------------------------------

@measurements_bp.route(
    "/<int:meas_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@customer_required
def edit_measurement(meas_id):
    measurement = (
        Measurement.query
        .filter_by(
            id=meas_id,
            customer_id=current_user.id,
        )
        .first_or_404()
    )

    if request.method == "POST":
        profile_name = request.form.get(
            "profile_name",
            "",
        ).strip()

        unit = request.form.get(
            "unit",
            "inches",
        ).strip().lower()

        notes = request.form.get(
            "notes",
            "",
        ).strip()

        is_default = (
            request.form.get("is_default")
            in {"on", "true", "1", "yes"}
        )

        if not profile_name:
            flash(
                "Profile name is required.",
                "danger",
            )

            return render_template(
                "customer/edit_measurement.html",
                measurement=measurement,
            )

        if unit not in {
            "inches",
            "inch",
            "cm",
            "centimeters",
        }:
            unit = "inches"

        measurement_values, error = (
            _parse_measurements(
                request.form,
                unit,
            )
        )

        if error:
            flash(error, "danger")

            return render_template(
                "customer/edit_measurement.html",
                measurement=measurement,
            )

        for field, value in measurement_values.items():
            setattr(
                measurement,
                field,
                value,
            )

        measurement.profile_name = (
            profile_name
        )
        measurement.unit = unit
        measurement.notes = (
            notes or None
        )

        if is_default:
            _set_default_profile(
                measurement
            )
        elif measurement.is_default:
            # Keep the current profile default unless
            # another profile is explicitly selected.
            measurement.is_default = True

        db.session.commit()

        flash(
            f'Measurement profile "{profile_name}" '
            "updated successfully!",
            "success",
        )

        return redirect(
            url_for(
                "measurements.list_measurements"
            )
        )

    return render_template(
        "customer/edit_measurement.html",
        measurement=measurement,
    )


# ------------------------------------------------------------
# Set default profile
# ------------------------------------------------------------

@measurements_bp.route(
    "/<int:meas_id>/set-default",
    methods=["POST"],
)
@login_required
@customer_required
def set_default_measurement(meas_id):
    measurement = (
        Measurement.query
        .filter_by(
            id=meas_id,
            customer_id=current_user.id,
        )
        .first_or_404()
    )

    _set_default_profile(
        measurement
    )

    db.session.commit()

    flash(
        f'"{measurement.profile_name}" is now '
        "your default measurement profile.",
        "success",
    )

    return redirect(
        url_for(
            "measurements.list_measurements"
        )
    )


# ------------------------------------------------------------
# Delete measurement profile
# ------------------------------------------------------------

@measurements_bp.route(
    "/<int:meas_id>/delete",
    methods=["POST"],
)
@login_required
@customer_required
def delete_measurement(meas_id):
    measurement = (
        Measurement.query
        .filter_by(
            id=meas_id,
            customer_id=current_user.id,
        )
        .first_or_404()
    )

    was_default = measurement.is_default

    db.session.delete(measurement)
    db.session.flush()

    # If the deleted profile was default, automatically
    # promote the newest remaining profile.
    if was_default:
        replacement = (
            Measurement.query
            .filter_by(
                customer_id=current_user.id,
            )
            .order_by(
                Measurement.created_at.desc()
            )
            .first()
        )

        if replacement:
            replacement.is_default = True

    db.session.commit()

    flash(
        "Measurement profile deleted.",
        "info",
    )

    return redirect(
        url_for(
            "measurements.list_measurements"
        )
    )


# ------------------------------------------------------------
# Measurement JSON
# ------------------------------------------------------------

@measurements_bp.route(
    "/<int:meas_id>/json"
)
@login_required
def get_measurement_json(meas_id):
    measurement = (
        Measurement.query
        .filter_by(id=meas_id)
        .first_or_404()
    )

    # Customers can only access their own measurements.
    # Tailors and admins may access a measurement when
    # needed for order fulfillment.
    if (
        measurement.customer_id != current_user.id
        and not current_user.is_tailor
        and not current_user.is_admin
    ):
        return jsonify({
            "error": "Unauthorized"
        }), 403

    return jsonify(
        measurement.to_dict()
    )