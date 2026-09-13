from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy  # pyright: ignore[reportMissingImports]


# ============================================================
# DATABASE
# ============================================================

db = SQLAlchemy()


# ============================================================
# LOGIN MANAGEMENT
# ============================================================

login_manager = LoginManager()

login_manager.login_view = "auth.login"  # pyright: ignore[reportAttributeAccessIssue]
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "info"


# ============================================================
# DATABASE INITIALIZATION HELPER
# ============================================================

def init_extensions(app):
    """
    Initialize Flask extensions.

    Keeping extension initialization in one place makes the
    application easier to maintain and test.
    """

    db.init_app(app)
    login_manager.init_app(app)

    return app


# ============================================================
# LOGIN USER LOADER
# ============================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Load the authenticated user from the database.

    Imports User here instead of at module import time to avoid
    circular-import problems between models.
    """

    if not user_id:
        return None

    try:
        from models.user import User

        user = db.session.get(
            User,
            int(user_id),
        )

        return user if user and user.is_active else None

    except (TypeError, ValueError):
        return None