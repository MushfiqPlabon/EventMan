from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    SECRET_KEY = config("SECRET_KEY")
except Exception:
    raise ValueError("SECRET_KEY environment variable is required but not set")

DEBUG = config("DEBUG", default="False").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS", default="").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
    if origin.strip()
]

INTERNAL_IPS = [
    ip.strip()
    for ip in config("INTERNAL_IPS", default="127.0.0.1").split(",")
    if ip.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",  # Required for GIN indexes and TrigramExtension
    "django.contrib.sites",
    "eventMan",  # Add eventMan app to INSTALLED_APPS
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "events",
    "cachalot",
]

# Add development-only apps when DEBUG is True
if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
        "django_extensions",
        "querycount",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# Add Debug Toolbar middleware as early as possible (but after WhiteNoise)
if DEBUG:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# Add other development-only middleware
if DEBUG:
    MIDDLEWARE += [
        "querycount.middleware.QueryCountMiddleware",
    ]

ROOT_URLCONF = "eventMan.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "eventMan.context_processors.email_verification_processor",
            ],
        },
    },
]

# Add debug context processor when DEBUG is True
if DEBUG:
    TEMPLATES[0]["OPTIONS"]["context_processors"].insert(
        0, "django.template.context_processors.debug"
    )

WSGI_APPLICATION = "eventMan.wsgi.app"
ASGI_APPLICATION = "eventMan.asgi.app"

DATABASES = {
    "default": (
        dj_database_url.parse(
            config("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
        if config("DATABASE_URL", default=None)
        else {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Additional WhiteNoise settings for production
if not DEBUG:
    # Disable WhiteNoise's use of static file finders in production
    WHITENOISE_USE_FINDERS = False
    # Disable auto-refresh in production
    WHITENOISE_AUTOREFRESH = False
else:
    # Enable for development
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default image path for events
EVENT_DEFAULT_IMAGE = config(
    "EVENT_DEFAULT_IMAGE", default="event_images/default_event.webp"
)

# Cache configuration (using django-cachalot for automatic ORM query caching)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # Use local memory cache for basic caching
    },
}


ACCOUNT_LOGIN_METHODS = ["email"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Login after email confirmation (default)
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "email2",
    "password1",
    "password2",
    "first_name",
    "last_name",
]
ACCOUNT_RATE_LIMITS = {"login_failed": "5/5m"}
ACCOUNT_FORMS = {
    "signup": "events.forms.CustomSignupForm",
    "login": "events.forms.CustomLoginForm",
}
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default="True").lower() == "true"
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=10, cast=int)

# Pagination settings
PARTICIPANT_DASHBOARD_PAGINATION = config(
    "PARTICIPANT_DASHBOARD_PAGINATION", default=10, cast=int
)
USER_ADMIN_PAGINATION = config("USER_ADMIN_PAGINATION", default=50, cast=int)
EVENT_IMAGE_MAX_SIZE = config(
    "EVENT_IMAGE_MAX_SIZE", default=5242880, cast=int
)  # 5MB by default

# Security settings (can be configured via environment variables)
SECURE_HSTS_SECONDS = config(
    "SECURE_HSTS_SECONDS", default=0, cast=int
)  # Set to 31536000 in production if using HTTPS
SECURE_SSL_REDIRECT = (
    config("SECURE_SSL_REDIRECT", default="True").lower() == "true"
)  # Set to true in production by default
SESSION_COOKIE_SECURE = (
    config("SESSION_COOKIE_SECURE", default="True").lower() == "true"
)  # Set to true in production by default
CSRF_COOKIE_SECURE = (
    config("CSRF_COOKIE_SECURE", default="True").lower() == "true"
)  # Set to true in production by default

# Additional security settings
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    config("SECURE_HSTS_INCLUDE_SUBDOMAINS", default="True").lower() == "true"
)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default="True").lower() == "true"
SECURE_CONTENT_TYPE_NOSNIFF = (
    config("SECURE_CONTENT_TYPE_NOSNIFF", default="True").lower() == "true"
)
SECURE_BROWSER_XSS_FILTER = (
    config("SECURE_BROWSER_XSS_FILTER", default="True").lower() == "true"
)
X_FRAME_OPTIONS = config("X_FRAME_OPTIONS", default="DENY")

SITE_ID = 1

# Debug Toolbar configuration
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }


def validate_required_configs():
    required_configs = ["SECRET_KEY", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD"]
    for config_name in required_configs:
        if not config(config_name, default=""):
            raise ValueError(f"Required configuration {config_name} is not set")


validate_required_configs()
