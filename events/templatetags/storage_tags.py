"""
Template tags for storage-related functionality.
"""

from django import template
from django.conf import settings

from ..storage_utils import storage_config

register = template.Library()


@register.simple_tag
def cloudinary_status():
    """Check if Cloudinary is properly configured and available."""
    return storage_config.validate_cloudinary_config()


@register.simple_tag
def get_storage_backend(storage_type="default"):
    """Get the current storage backend for the specified type."""
    backends = storage_config.get_storage_backends()
    return backends.get(storage_type, {}).get("BACKEND", "Unknown")


@register.inclusion_tag("events/_storage_status.html")
def storage_status():
    """Display storage configuration status."""
    return {
        "cloudinary_available": storage_config.validate_cloudinary_config(),
        "debug": settings.DEBUG,
        "storage_backends": storage_config.get_storage_backends(),
    }
