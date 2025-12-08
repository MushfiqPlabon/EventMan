from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-fallback-key")

DEBUG = config("DEBUG", default="False").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS", default="").split(",")
    if host.strip()
] or ["*"]

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
    "django.contrib.sites",
    "eventMan", # Add eventMan app to INSTALLED_APPS
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "events",
    "debug_toolbar",
    "cachalot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default image path for events
EVENT_DEFAULT_IMAGE = config(
    "EVENT_DEFAULT_IMAGE", default="event_images/default_event.webp"
)

# Cache timeout settings (in seconds)
CATEGORY_CACHE_TIMEOUT = config("CATEGORY_CACHE_TIMEOUT", default=300, cast=int)
DASHBOARD_CACHE_TIMEOUT = config("DASHBOARD_CACHE_TIMEOUT", default=300, cast=int)
USER_GROUPS_CACHE_TIMEOUT = config("USER_GROUPS_CACHE_TIMEOUT", default=300, cast=int)

ACCOUNT_LOGIN_METHODS = ["email"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "email2",
    "password1",
    "password2",
    "first_name",
    "last_name",
]
ACCOUNT_RATE_LIMITS = {"login_failed": "5/5m"}
ACCOUNT_FORMS = {"signup": "events.forms.CustomSignupForm"}
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default="True").lower() == "true"
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)

SITE_ID = 1

# Django-Cachalot settings
CACHALOT_ENABLED = True
CACHALOT_TIMEOUT = 60 * 60 * 24  # Cache for 24 hours by default
