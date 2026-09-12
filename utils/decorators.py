from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*allowed_roles):
    """Decorator to enforce that current_user has one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please sign in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in allowed_roles:
                flash('You do not have permission to access that resource.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def customer_required(f):
    """Ensure current user is authenticated and has role 'customer'."""
    return role_required('customer')(f)


def tailor_required(f):
    """Ensure current user is authenticated and has role 'tailor'."""
    return role_required('tailor')(f)


def admin_required(f):
    """Ensure current user is authenticated and has role 'admin'."""
    return role_required('admin')(f)
