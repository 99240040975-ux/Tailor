import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from models import db
from models.user import User
from config import config
from utils.helpers import get_unread_count, format_currency, format_date


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure upload directories exist
    for folder in ['profile', 'reference', 'documents']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder), exist_ok=True)

    # Init extensions
    db.init_app(app)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Template context processors and filters
    @app.context_processor
    def inject_globals():
        unread = 0
        if current_user.is_authenticated:
            unread = get_unread_count(current_user.id)
        return {
            'now': datetime.utcnow(),
            'unread_messages_count': unread
        }

    @app.template_filter('currency')
    def currency_filter(val):
        return format_currency(val)

    @app.template_filter('date')
    def date_filter(val, fmt='%b %d, %Y'):
        return format_date(val, fmt)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.tailor import tailor_bp
    from routes.admin import admin_bp
    from routes.orders import orders_bp
    from routes.measurements import measurements_bp
    from routes.reviews import reviews_bp
    from routes.locations import locations_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(tailor_bp, url_prefix='/tailor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(measurements_bp, url_prefix='/measurements')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')

    # Root route
    @app.route('/')
    def index():
        from models.tailor import Tailor
        from models.review import Review
        try:
            featured_tailors = Tailor.query.filter_by(availability=True).order_by(
                Tailor.rating.desc()
            ).limit(6).all()
            recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(4).all()
        except Exception:
            featured_tailors = []
            recent_reviews = []
        return render_template('index.html',
                               featured_tailors=featured_tailors,
                               recent_reviews=recent_reviews)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app


app = create_app()

with app.app_context():
    try:
        db.create_all()
    except Exception as err:
        app.logger.warning(f"Database init notice: {err}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
