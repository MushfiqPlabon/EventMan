import os
from datetime import timedelta
from pathlib import Path

import cloudinary
import cloudinary.uploader
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-your-secret-key-here")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third party apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "debug_toolbar",
    # FREE packages for code reduction
    "django_htmx",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "cloudinary_storage",  # Add Cloudinary storage
    "cloudinary",  # Add Cloudinary
    # Local apps
    "events",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_htmx.middleware.HtmxMiddleware",  # HTMX middleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "eventMan.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "eventMan.wsgi.app"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL)

# Connection pooling for production
if not DEBUG:
    if (
        "default" in DATABASES
        and "ENGINE" in DATABASES["default"]
        and "postgresql" in DATABASES["default"]["ENGINE"]
    ):
        DATABASES["default"]["CONN_MAX_AGE"] = 600
        DATABASES["default"]["OPTIONS"] = {
            "sslmode": "require",
            "application_name": "EventMan",
        }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
)

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Sites framework
SITE_ID = 1

# Allauth settings
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

# Email settings
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="webmaster@localhost")

# Debug toolbar settings
if DEBUG:
    INTERNAL_IPS = config("INTERNAL_IPS", default="127.0.0.1").split(",")

# Crispy forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"  # Ensure a custom 'tailwind' template pack is configured or use a standard one like 'bootstrap5'
CRISPY_TEMPLATE_PACK = "tailwind"

# Custom crispy forms field template
CRISPY_FIELD_TEMPLATE = "tailwind/field.html"
CRISPY_LABEL_CLASS = "form-label"
CRISPY_FIELD_CLASS = "form-input"

# HTMX settings
HTMX_REQUIRE_CSRF = True

# ===== PRODUCTION SETTINGS =====
# Production environment detection
IS_RENDER = os.environ.get("RENDER") == "true" # Check for Render environment variable

if IS_RENDER:
    # Production settings for Render
    DEBUG = False

    # Render domains
    ALLOWED_HOSTS = [
        "eventman-phi-assign.onrender.com", # Add the Render domain
        "localhost",
        "127.0.0.1",
    ]

    # Add custom domain if provided (Render also supports custom domains)
    RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

    # Static files configuration for Render
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]

    # Media files configuration
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    # Security settings for production
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # CSRF settings for Render
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        "https://*.onrender.com",
    ]

    # Logging configuration for Render
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }

# ===== REDIS CONFIGURATION (UPSTASH) =====
# Redis settings for caching and real-time features
REDIS_URL = config("REDIS_URL", default="")


if REDIS_URL:
    # Configure Django cache with Redis
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"{REDIS_URL}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "ssl_cert_reqs": None,
                },
            },
        }
    }

    # Use Redis for sessions (optional)
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    # Cache timeout settings
    CACHE_TTL = 60 * 15  # 15 minutes

else:
    # Fallback to default cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# JWT Settings (from .env)
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = config(
    "JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60, cast=int
)
JWT_REFRESH_TOKEN_LIFETIME_DAYS = config(
    "JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=1, cast=int
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=JWT_ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=JWT_REFRESH_TOKEN_LIFETIME_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}
