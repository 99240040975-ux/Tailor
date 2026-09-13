from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*allowed_roles):
    """
    Require authentication and one of the supplied roles.

    Example:
        @role_required("admin", "tailor")
        def dashboard():
            ...
    """

    normalized_roles = {
        str(role).strip().lower()
        for role in allowed_roles
        if role
    }

    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(
                    "Please sign in to access this page.",
                    "warning",
                )
                return redirect(
                    url_for(
                        "auth.login",
                        next=request_path(),
                    )
                )

            user_role = str(
                getattr(current_user, "role", "")
            ).strip().lower()

            if user_role not in normalized_roles:
                flash(
                    "You do not have permission to access "
                    "that resource.",
                    "danger",
                )
                return redirect(url_for("index"))

            if not getattr(current_user, "is_active", True):
                flash(
                    "Your account is currently inactive.",
                    "warning",
                )
                return redirect(url_for("auth.logout"))

            return view_function(*args, **kwargs)

        return decorated_function

    return decorator


def request_path():
    """Return the current request path safely."""
    try:
        from flask import request

        path = request.full_path

        if path.endswith("?"):
            path = path[:-1]

        return path
    except RuntimeError:
        return "/"


def customer_required(view_function):
    """Require an authenticated customer."""
    return role_required("customer")(view_function)


def tailor_required(view_function):
    """Require an authenticated tailor."""
    return role_required("tailor")(view_function)


def admin_required(view_function):
    """Require an authenticated administrator."""
    return role_required("admin")(view_function)


def customer_or_admin_required(view_function):
    """Require either a customer or administrator."""
    return role_required(
        "customer",
        "admin",
    )(view_function)


def tailor_or_admin_required(view_function):
    """Require either a tailor or administrator."""
    return role_required(
        "tailor",
        "admin",
    )(view_function)


def any_authenticated_required(view_function):
    """Require any active authenticated account."""
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(
                "Please sign in to access this page.",
                "warning",
            )
            return redirect(
                url_for(
                    "auth.login",
                    next=request_path(),
                )
            )

        if not getattr(current_user, "is_active", True):
            flash(
                "Your account is currently inactive.",
                "warning",
            )
            return redirect(url_for("auth.logout"))

        return view_function(*args, **kwargs)
    return decorated_function