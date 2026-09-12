from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.tailor import Tailor
from utils.validators import validate_email, validate_password, validate_phone

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_tailor:
            return redirect(url_for('tailor.dashboard'))
        return redirect(url_for('customer.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        valid, err = validate_email(email)
        if not valid:
            flash(err, 'danger')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

        if not user.is_active_account:
            flash('This account has been deactivated. Please contact support.', 'warning')
            return render_template('login.html', email=email)

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.name}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif user.is_tailor:
            return redirect(url_for('tailor.dashboard'))
        return redirect(url_for('customer.dashboard'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'customer').lower()

        # Specific tailor fields
        shop_name = request.form.get('shop_name', '').strip()
        city = request.form.get('city', '').strip()
        specialization = request.form.get('specialization', '').strip()

        if role not in ['customer', 'tailor']:
            role = 'customer'

        # Validations
        if not name or len(name) < 2:
            flash('Please enter your full name.', 'danger')
            return render_template('register.html', **request.form)

        valid_e, err_e = validate_email(email)
        if not valid_e:
            flash(err_e, 'danger')
            return render_template('register.html', **request.form)

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html', **request.form)

        valid_p, err_p = validate_password(password)
        if not valid_p:
            flash(err_p, 'danger')
            return render_template('register.html', **request.form)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', **request.form)

        valid_ph, err_ph = validate_phone(phone)
        if not valid_ph:
            flash(err_ph, 'danger')
            return render_template('register.html', **request.form)

        if role == 'tailor' and not shop_name:
            flash('Shop or studio name is required for tailors.', 'danger')
            return render_template('register.html', **request.form)

        # Create user
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            role=role
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # If tailor, create tailor profile
        if role == 'tailor':
            tailor_profile = Tailor(
                user_id=new_user.id,
                shop_name=shop_name or f"{name}'s Atelier",
                city=city or 'City Center',
                specialization=specialization or 'Custom Tailoring & Alterations',
                experience=1,
                price_range='₹300 - ₹2000',
                availability=True
            )
            db.session.add(tailor_profile)

        db.session.commit()
        login_user(new_user)
        flash('Account created successfully! Welcome to Local Tailor Connect.', 'success')

        if new_user.is_tailor:
            return redirect(url_for('tailor.dashboard'))
        return redirect(url_for('customer.dashboard'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))
