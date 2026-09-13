import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DATABASE
# ============================================================

raw_database_url = os.getenv("DATABASE_URL", "").strip()

if raw_database_url:
    # Render and some older PostgreSQL providers may return
    # postgres:// instead of postgresql://.
    if raw_database_url.startswith("postgres://"):
        DATABASE_URL = raw_database_url.replace(
            "postgres://",
            "postgresql://",
            1,
        )
    else:
        DATABASE_URL = raw_database_url
else:
    # Zero-configuration local development.
    DATABASE_URL = (
        f"sqlite:///{BASE_DIR / 'local_tailor_connect.db'}"
    )


def is_sqlite_database():
    return DATABASE_URL.lower().startswith("sqlite")


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

class Config:

    # --------------------------------------------------------
    # Flask
    # --------------------------------------------------------

    SECRET_KEY = os.getenv("SECRET_KEY")

    DEBUG = False
    TESTING = False

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if is_sqlite_database():
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

    # --------------------------------------------------------
    # Uploads
    # --------------------------------------------------------

    UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads"
    )

    MAX_CONTENT_LENGTH = int(
        os.getenv(
            "MAX_CONTENT_LENGTH",
            16 * 1024 * 1024,
        )
    )

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp",
    }

    ALLOWED_DOCUMENT_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
    }

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    TAILORS_PER_PAGE = int(
        os.getenv("TAILORS_PER_PAGE", "12")
    )

    ORDERS_PER_PAGE = int(
        os.getenv("ORDERS_PER_PAGE", "10")
    )

    MESSAGES_PER_PAGE = int(
        os.getenv("MESSAGES_PER_PAGE", "20")
    )

    # --------------------------------------------------------
    # Application identity
    # --------------------------------------------------------

    APP_NAME = "TailorConnect"

    APP_TAGLINE = (
        "Discover local tailors. "
        "Design your fit. "
        "Track every stitch."
    )

    APP_VERSION = "2.0.0"

    # --------------------------------------------------------
    # Session / security
    # --------------------------------------------------------

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # HTTPS is enabled automatically on Render.
    # Keep this configurable so local HTTP development works.
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        == "true"
    )

    # --------------------------------------------------------
    # Upload folders
    # --------------------------------------------------------

    PROFILE_UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads" / "profile"
    )

    REFERENCE_UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads" / "reference"
    )

    DOCUMENT_UPLOAD_FOLDER = str(
        BASE_DIR / "static" / "uploads" / "documents"
    )

    # --------------------------------------------------------
    # Location system
    # --------------------------------------------------------

    LOCATION_DATA_FOLDER = str(
        BASE_DIR / "data"
    )

    INDIA_LOCATIONS_FILE = str(
        BASE_DIR
        / "data"
        / "india_locations.json"
    )

    # --------------------------------------------------------
    # Order lifecycle
    # --------------------------------------------------------

    ORDER_STATUSES = [
        "pending",
        "quoted",
        "confirmed",
        "cutting",
        "stitching",
        "alteration",
        "quality_check",
        "ready",
        "delivered",
    ]

    # --------------------------------------------------------
    # User roles
    # --------------------------------------------------------

    USER_ROLES = {
        "customer",
        "tailor",
        "admin",
    }

    # --------------------------------------------------------
    # Default application settings
    # --------------------------------------------------------

    DEFAULT_MEASUREMENT_UNIT = "cm"

    DEFAULT_ORDER_STATUS = "pending"

    DEFAULT_DELIVERY_METHOD = "Pickup"


# ============================================================
# DEVELOPMENT
# ============================================================

class DevelopmentConfig(Config):

    DEBUG = True
    TESTING = False

    SESSION_COOKIE_SECURE = False
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "local-development-secret-key",
    )


# ============================================================
# TESTING
# ============================================================

class TestingConfig(Config):

    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///:memory:"
    )

    SQLALCHEMY_ENGINE_OPTIONS = {}

    SESSION_COOKIE_SECURE = False
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "test-secret-key",
    )


# ============================================================
# PRODUCTION
# ============================================================

class ProductionConfig(Config):

    DEBUG = False
    TESTING = False

    # Render uses HTTPS.
    SESSION_COOKIE_SECURE = True


# ============================================================
# CONFIGURATION SELECTOR
# ============================================================

environment = os.getenv(
    "FLASK_ENV",
    "production" if os.getenv("RENDER") else "development",
).lower()


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": ProductionConfig
    if os.getenv("RENDER")
    else DevelopmentConfig,
}


# ============================================================
# DIRECTORY INITIALIZATION
# ============================================================

UPLOAD_DIRECTORIES = [
    Config.UPLOAD_FOLDER,
    Config.PROFILE_UPLOAD_FOLDER,
    Config.REFERENCE_UPLOAD_FOLDER,
    Config.DOCUMENT_UPLOAD_FOLDER,
]

for directory in UPLOAD_DIRECTORIES:
    os.makedirs(directory, exist_ok=True)