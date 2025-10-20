"""
Centralized storage utilities for EventMan.
Handles Cloudinary integration with WhiteNoise fallback.
"""

import logging
from typing import Dict

import cloudinary
from decouple import config
from django.conf import settings

logger = logging.getLogger(__name__)


class StorageConfig:
    """Centralized storage configuration management."""

    def __init__(self):
        self._cloudinary_configured = None
        self._config_validated = False

    def validate_cloudinary_config(self) -> bool:
        """Validate Cloudinary configuration."""
        if self._cloudinary_configured is not None:
            return self._cloudinary_configured

        # Check if Cloudinary is explicitly disabled
        cloudinary_enabled = config("CLOUDINARY_ENABLED", default=True, cast=bool)
        if not cloudinary_enabled:
            logger.info("Cloudinary is disabled via CLOUDINARY_ENABLED=false")
            self._cloudinary_configured = False
            return False

        required_vars = [
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
        ]
        missing_vars = []

        for var in required_vars:
            value = config(var, default=None)
            if not value:
                missing_vars.append(var)

        if missing_vars:
            logger.warning(
                f"Missing Cloudinary configuration: {', '.join(missing_vars)}"
            )
            self._cloudinary_configured = False
        else:
            try:
                # Test Cloudinary configuration
                cloudinary.config(
                    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
                    api_key=config("CLOUDINARY_API_KEY"),
                    api_secret=config("CLOUDINARY_API_SECRET"),
                    secure=True,
                )
                # Light validation - just check if credentials are set
                # Skip API call for faster startup
                self._cloudinary_configured = True
                logger.info("Cloudinary configuration validated successfully")
            except Exception as e:
                logger.error(f"Cloudinary configuration error: {e}")
                self._cloudinary_configured = False

        return self._cloudinary_configured

    def get_storage_backends(self) -> Dict[str, Dict[str, str]]:
        """Get appropriate storage backends based on environment and configuration."""
        is_cloudinary_available = self.validate_cloudinary_config()
        is_production = not settings.DEBUG
        force_whitenoise = config("FORCE_WHITENOISE", default=False, cast=bool)

        # Media storage strategy
        if is_cloudinary_available and not force_whitenoise:
            media_backend = "cloudinary_storage.storage.MediaCloudinaryStorage"
        else:
            media_backend = "django.core.files.storage.FileSystemStorage"

        # Static files storage strategy
        if is_production and is_cloudinary_available and not force_whitenoise:
            # Production with Cloudinary: Use Cloudinary for static files
            static_backend = "cloudinary_storage.storage.StaticHashedCloudinaryStorage"
        else:
            # Development, Cloudinary unavailable, or forced WhiteNoise: Use WhiteNoise
            if is_production:
                static_backend = (
                    "whitenoise.storage.CompressedManifestStaticFilesStorage"
                )
            else:
                static_backend = "django.contrib.staticfiles.storage.StaticFilesStorage"

        logger.info(
            f"Storage configuration: Media={media_backend}, Static={static_backend}"
        )

        return {
            "default": {"BACKEND": media_backend},
            "staticfiles": {"BACKEND": static_backend},
        }

    def get_middleware_config(self) -> list:
        """Get appropriate middleware configuration."""
        middleware = [
            "django.middleware.security.SecurityMiddleware",
        ]

        # Add WhiteNoise if not using Cloudinary for static files or in development
        is_cloudinary_available = self.validate_cloudinary_config()
        is_production = not settings.DEBUG

        if not (is_production and is_cloudinary_available):
            middleware.append("whitenoise.middleware.WhiteNoiseMiddleware")

        middleware.extend(
            [
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "allauth.account.middleware.AccountMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ]
        )

        # Add debug toolbar in development
        if settings.DEBUG:
            middleware.append("debug_toolbar.middleware.DebugToolbarMiddleware")

        # Add HTMX middleware
        middleware.append("django_htmx.middleware.HtmxMiddleware")

        return middleware


# Global storage configuration instance
storage_config = StorageConfig()


def configure_cloudinary() -> bool:
    """Configure Cloudinary with proper error handling."""
    try:
        if storage_config.validate_cloudinary_config():
            cloudinary.config(
                cloud_name=config("CLOUDINARY_CLOUD_NAME"),
                api_key=config("CLOUDINARY_API_KEY"),
                api_secret=config("CLOUDINARY_API_SECRET"),
                secure=True,
            )
            return True
    except Exception as e:
        logger.error(f"Failed to configure Cloudinary: {e}")

    return False
