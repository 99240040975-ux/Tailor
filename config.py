import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Format database URL (handles Render postgres:// -> postgresql:// and SQLite fallback)
_raw_db_url = os.environ.get('DATABASE_URL')
if _raw_db_url:
    if _raw_db_url.startswith('postgres://'):
        _db_uri = _raw_db_url.replace('postgres://', 'postgresql://', 1)
    else:
        _db_uri = _raw_db_url
else:
    _db_uri = f"sqlite:///{os.path.join(BASE_DIR, 'local_tailor_connect.db')}"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tailor-connect-production-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = _db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dynamic engine options
    if 'sqlite' in _db_uri.lower():
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }

    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx'}

    # Pagination
    TAILORS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10
    MESSAGES_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig if os.environ.get('RENDER') else DevelopmentConfig,
}
