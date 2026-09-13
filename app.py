import os
from datetime import datetime

from flask import Flask, render_template
from flask_login import current_user

from config import config
from models import db, init_extensions
from models.user import User
from utils.helpers import format_currency, format_date, get_unread_count


def create_app(config_name=None):
    """Application factory for TailorConnect."""

    if config_name is None:
        config_name = os.environ.get(
            "FLASK_ENV",
            "development",
        )

    selected_config = config.get(
        config_name,
        config["default"],
    )

    if config_name == "production" and not selected_config.SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY must be set when running in production."
        )

    app = Flask(__name__)
    app.config.from_object(selected_config)

    # ------------------------------------------------------------------
    # Upload directories
    # ------------------------------------------------------------------
    upload_root = app.config.get("UPLOAD_FOLDER")

    if not upload_root:
        upload_root = os.path.join(
            app.root_path,
            "static",
            "uploads",
        )
        app.config["UPLOAD_FOLDER"] = upload_root

    for folder in (
        "profile",
        "reference",
        "documents",
    ):
        os.makedirs(
            os.path.join(upload_root, folder),
            exist_ok=True,
        )

    # ------------------------------------------------------------------
    # Flask extensions
    # ------------------------------------------------------------------
    init_extensions(app)

    # ------------------------------------------------------------------
    # Import every model before database creation.
    # ------------------------------------------------------------------
    from models.tailor import Tailor
    from models.measurement import Measurement
    from models.message import Message
    from models.order import Order
    from models.review import Review
    from models.location import (
        State,
        District,
        Taluk,
        City,
        Town,
        Village,
        Locality,
    )

    # Keep model references loaded for SQLAlchemy.
    _ = (
        User,
        Tailor,
        Measurement,
        Message,
        Order,
        Review,
        State,
        District,
        Taluk,
        City,
        Town,
        Village,
        Locality,
    )

    # ------------------------------------------------------------------
    # Template context
    # ------------------------------------------------------------------
    @app.context_processor
    def inject_globals():
        unread_count = 0

        try:
            if current_user.is_authenticated:
                unread_count = get_unread_count(
                    current_user.id
                )
        except Exception:
            unread_count = 0

        return {
            "now": datetime.utcnow(),
            "unread_messages_count": unread_count,
        }

    # ------------------------------------------------------------------
    # Template filters
    # ------------------------------------------------------------------
    @app.template_filter("currency")
    def currency_filter(value):
        return format_currency(value)

    @app.template_filter("date")
    def date_filter(value, fmt="%b %d, %Y"):
        return format_date(value, fmt)

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.tailor import tailor_bp
    from routes.admin import admin_bp
    from routes.orders import orders_bp
    from routes.measurements import measurements_bp
    from routes.reviews import reviews_bp
    from routes.locations import locations_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/auth",
    )

    app.register_blueprint(
        customer_bp,
        url_prefix="/customer",
    )

    app.register_blueprint(
        tailor_bp,
        url_prefix="/tailor",
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin",
    )

    app.register_blueprint(
        orders_bp,
        url_prefix="/orders",
    )

    app.register_blueprint(
        measurements_bp,
        url_prefix="/measurements",
    )

    app.register_blueprint(
        reviews_bp,
        url_prefix="/reviews",
    )

    app.register_blueprint(
        locations_bp,
        url_prefix="/api/locations",
    )

    # ------------------------------------------------------------------
    # Home page
    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        try:
            featured_tailors = (
                Tailor.query
                .filter_by(is_active=True)
                .order_by(
                    Tailor.is_verified.desc(),
                    Tailor.rating.desc(),
                    Tailor.total_reviews.desc(),
                )
                .limit(6)
                .all()
            )

            recent_reviews = (
                Review.query
                .order_by(
                    Review.created_at.desc()
                )
                .limit(4)
                .all()
            )

        except Exception as exc:
            app.logger.warning(
                "Could not load homepage data: %s",
                exc,
            )

            featured_tailors = []
            recent_reviews = []

        return render_template(
            "index.html",
            featured_tailors=featured_tailors,
            recent_reviews=recent_reviews,
        )

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    @app.route("/health")
    def health_check():
        return {
            "status": "ok",
            "service": "TailorConnect",
        }

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return (
            render_template("404.html"),
            404,
        )

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception(
            "Unhandled server error"
        )

        return (
            render_template("500.html"),
            500,
        )

    return app


# ----------------------------------------------------------------------
# Application instance
# ----------------------------------------------------------------------
app = create_app()


# ----------------------------------------------------------------------
# Database initialization
#
# create_all() only creates missing tables.
# It does NOT replace or migrate existing tables.
# Existing schema changes are handled separately by migrations.
# ----------------------------------------------------------------------
with app.app_context():
    try:
        db.create_all()

        app.logger.info(
            "Database tables checked successfully."
        )

    except Exception as exc:
        app.logger.warning(
            "Database initialization notice: %s",
            exc,
        )


# ----------------------------------------------------------------------
# Development server
# ----------------------------------------------------------------------
if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            5000,
        )
    )

    app.run(
        debug=app.config.get("DEBUG", True),
        host="0.0.0.0",
        port=port,
    )