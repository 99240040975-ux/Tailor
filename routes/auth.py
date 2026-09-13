from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models import db
from models.tailor import Tailor
from models.user import User
from utils.validators import validate_email, validate_password, validate_phone


auth_bp = Blueprint("auth", __name__)


def _safe_next_url():
    """Return a safe local redirect target from ?next=."""
    next_page = request.args.get("next", "").strip()

    if not next_page:
        return None

    parsed = urlparse(next_page)

    if parsed.scheme or parsed.netloc:
        return None

    if not next_page.startswith("/"):
        return None

    return next_page


def _dashboard_redirect(user):
    """Send the authenticated user to the correct dashboard."""
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))

    if user.is_tailor:
        return redirect(url_for("tailor.dashboard"))

    return redirect(url_for("customer.dashboard"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _dashboard_redirect(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") in {
            "on",
            "true",
            "1",
            "yes",
        }

        valid, error = validate_email(email)

        if not valid:
            flash(error or "Invalid email address.", "danger")
            return render_template(
                "login.html",
                email=email,
            )

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash(
                "Invalid email or password. Please try again.",
                "danger",
            )
            return render_template(
                "login.html",
                email=email,
            )

        if not user.is_active:
            flash(
                "This account has been deactivated. Please contact support.",
                "warning",
            )
            return render_template(
                "login.html",
                email=email,
            )

        login_user(
            user,
            remember=remember,
        )

        flash(
            f"Welcome back, {user.name}!",
            "success",
        )

        next_page = _safe_next_url()

        if next_page:
            return redirect(next_page)

        return _dashboard_redirect(user)

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            "",
        )
        phone = request.form.get("phone", "").strip()

        role = request.form.get(
            "role",
            "customer",
        ).strip().lower()

        # Tailor information
        shop_name = request.form.get(
            "shop_name",
            "",
        ).strip()

        city = request.form.get(
            "city",
            "",
        ).strip()

        specialization = request.form.get(
            "specialization",
            "",
        ).strip()

        address = request.form.get(
            "address",
            "",
        ).strip()

        # Location hierarchy values are accepted from the form.
        # They can be connected to the Tailor model when the
        # location fields are included in the model schema.
        state_id = request.form.get(
            "state_id",
            type=int,
        )

        district_id = request.form.get(
            "district_id",
            type=int,
        )

        taluk_id = request.form.get(
            "taluk_id",
            type=int,
        )

        city_id = request.form.get(
            "city_id",
            type=int,
        )

        town_id = request.form.get(
            "town_id",
            type=int,
        )

        village_id = request.form.get(
            "village_id",
            type=int,
        )

        # Coordinates
        latitude = None
        longitude = None

        latitude_value = request.form.get(
            "latitude",
            "",
        ).strip()

        longitude_value = request.form.get(
            "longitude",
            "",
        ).strip()

        try:
            if latitude_value:
                latitude = float(latitude_value)

            if longitude_value:
                longitude = float(longitude_value)

        except ValueError:
            flash(
                "Please provide valid location coordinates.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        if role not in {"customer", "tailor"}:
            role = "customer"

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not name or len(name) < 2:
            flash(
                "Please enter your full name.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        valid_email, email_error = validate_email(email)

        if not valid_email:
            flash(
                email_error or "Invalid email address format.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "An account with this email already exists.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        valid_password, password_error = validate_password(
            password
        )

        if not valid_password:
            flash(
                password_error or "Invalid password.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        valid_phone, phone_error = validate_phone(phone)

        if not valid_phone:
            flash(
                phone_error or "Invalid phone number.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        if role == "tailor" and not shop_name:
            flash(
                "Shop or studio name is required for tailors.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        if request.form.get("terms") not in {"1", "on", "true", "yes"}:
            flash(
                "Please accept the platform terms before registering.",
                "danger",
            )
            return render_template(
                "register.html",
                **request.form,
            )

        # --------------------------------------------------
        # Create user
        # --------------------------------------------------

        new_user = User()
        new_user.name = name
        new_user.email = email
        new_user.phone = phone
        new_user.role = role
        new_user.is_active = True

        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.flush()

            # --------------------------------------------------
            # Create tailor profile
            #
            # Only fields currently present in models/tailor.py
            # are written here.
            # --------------------------------------------------

            if role == "tailor":
                tailor_profile = Tailor(
                    user_id=new_user.id,
                    shop_name=(
                        shop_name
                        or f"{name}'s Atelier"
                    ),
                    specialization=(
                        specialization
                        or "Custom Tailoring & Alterations"
                    ),
                    address=address or None,
                    city=city or "Tamil Nadu",
                    state_id=state_id,
                    district_id=district_id,
                    taluk_id=taluk_id,
                    city_id=city_id,
                    town_id=town_id,
                    village_id=village_id,
                    latitude=latitude,
                    longitude=longitude,
                    description=(
                        "Local tailoring and alteration services."
                    ),
                    experience=1,
                    price_range="₹300 - ₹2000",
                    availability="Available",
                    rating=0,
                    total_reviews=0,
                    is_verified=True,
                    is_active=True,
                )

                db.session.add(tailor_profile)

            db.session.commit()

        except Exception:
            db.session.rollback()

            flash(
                "We couldn't create your account right now. "
                "Please try again.",
                "danger",
            )

            return render_template(
                "register.html",
                **request.form,
            )

        # --------------------------------------------------
        # Log the user in
        # --------------------------------------------------

        login_user(new_user)

        flash(
            "Account created successfully! "
            "Welcome to TailorConnect.",
            "success",
        )

        return _dashboard_redirect(new_user)

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "You have been logged out safely.",
        "info",
    )

    return redirect(url_for("index"))