"""
Signal handlers for automatically creating user profiles.
"""

import logging

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created."""
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            # Log the error if profile creation fails and raise the exception
            logger.error(
                f"Failed to create user profile for user {instance.id}: {str(e)}"
            )
            raise  # Re-raise the exception to prevent silent failures
