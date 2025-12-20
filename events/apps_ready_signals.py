"""
Signal handlers that run when the events app is ready.
This is used to delay execution of database operations until after the app registry is fully loaded.
"""

from django.apps import apps
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate


def create_default_groups(sender, **kwargs):
    """
    Create default groups during app initialization.
    This function is called after the database is ready to avoid AppRegistryNotReady errors.
    """
    # Create default groups automatically (excluding Participant since it's handled in forms.py)
    Group.objects.get_or_create(name="Admin")
    Group.objects.get_or_create(name="Organizer")
    # Note: Participant group is handled in CustomSignupForm with caching for performance


def connect_signals():
    """Connect the post_migrate signal to create default groups after migrations."""
    # Connect the signal to run after migrations
    post_migrate.connect(create_default_groups, sender=apps.get_app_config("events"))


# Connect the signals when this module is imported
connect_signals()
