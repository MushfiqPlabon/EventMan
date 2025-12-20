import logging
import queue
import threading

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import get_connection, send_mail
from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

# Import EventParticipant at module level for signal registration
from .models import (Category, DashboardStats, Event, EventParticipant,
                     UserProfile)

User = get_user_model()

# Create a thread-safe queue for email tasks
email_queue = queue.Queue()
# Limit the number of concurrent email threads to prevent resource exhaustion
MAX_EMAIL_THREADS = getattr(settings, "MAX_EMAIL_THREADS", 5)


def _send_email_async(subject, plain_message, from_email, to_email, html_message):
    """Helper to send email in a separate thread with rate limiting."""

    def send():
        try:
            # Use a connection pool to manage SMTP connections efficiently
            connection = get_connection()
            send_mail(
                subject,
                plain_message,
                from_email,
                to_email,
                html_message=html_message,
                connection=connection,
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Async email failed: {str(e)}")

    # Limit the number of concurrent email threads to prevent resource exhaustion
    active_threads = threading.active_count()
    max_threads = (
        MAX_EMAIL_THREADS + 50
    )  # Allow some extra threads for other operations

    if active_threads < max_threads:
        thread = threading.Thread(target=send)
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
    else:
        # Log if we're skipping email due to too many active threads
        logger = logging.getLogger(__name__)
        logger.warning("Skipping email send due to high thread count")


def _get_email_content(user, event, is_cancellation=False):
    """Helper function to prepare email content."""
    template = (
        "emails/rsvp_cancellation.html"
        if is_cancellation
        else "emails/rsvp_confirmation.html"
    )
    action = "Cancellation" if is_cancellation else "Confirmation"
    subject = f"RSVP {action} for: {event.name}"

    html_message = render_to_string(template, {"user": user, "event": event})
    plain_message = strip_tags(html_message)
    from_email = (
        settings.DEFAULT_FROM_EMAIL
        or settings.EMAIL_HOST_USER
        or "noreply@yourdomain.com"
    )
    to_email = [user.email]
    return subject, plain_message, html_message, from_email, to_email


# Pre-save signal to capture old values for atomic integrity updates
@receiver(pre_save, sender=Event)
def capture_old_event_values(sender, instance, **kwargs):
    """Capture old values (date, category, organizer) before event is updated."""
    if instance.pk:
        try:
            old_instance = Event.objects.get(pk=instance.pk)
            instance._old_values = {
                "date": old_instance.date,
                "category_id": old_instance.category_id,
                "organizer_id": old_instance.organizer_id,
            }
        except Event.DoesNotExist:
            instance._old_values = {}
    else:
        instance._old_values = {}


@receiver(post_save, sender=EventParticipant)
def send_rsvp_email_notification(sender, instance, created, **kwargs):
    """Sends an async email notification when a user RSVPs."""
    if created:
        subject, plain_message, html_message, from_email, to_email = _get_email_content(
            instance.user, instance.event
        )
        _send_email_async(subject, plain_message, from_email, to_email, html_message)


@receiver(post_delete, sender=EventParticipant)
def send_rsvp_cancellation_notification(sender, instance, **kwargs):
    """Sends an async email notification when a user cancels RSVP."""
    subject, plain_message, html_message, from_email, to_email = _get_email_content(
        instance.user, instance.event, is_cancellation=True
    )
    _send_email_async(subject, plain_message, from_email, to_email, html_message)


# Signal-based dashboard counters


@receiver(post_save, sender=EventParticipant)
def update_participant_counters_on_save(sender, instance, created, **kwargs):
    """
    Updates participant counters when users RSVP to events.
    For O(1) dashboard access without expensive aggregation queries.
    """
    if created:  # Only when a new RSVP is created
        try:
            # Use atomic update with F expressions for thread-safe counter updates
            # Atomically update the participant count using F() expressions
            Event.objects.filter(pk=instance.event.pk).update(
                participant_count=F("participant_count") + 1
            )

            # Update user participation count
            UserProfile.objects.update_or_create(
                user=instance.user,
                defaults={"participation_count": F("participation_count") + 1},
            )
        except Exception as e:
            # Log error if updating participant counters fails
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Error updating participant counters for event {instance.event.pk}: {str(e)}"
            )


@receiver(post_delete, sender=EventParticipant)
def update_participant_counters_on_delete(sender, instance, **kwargs):
    """
    Updates participant counters when users cancel RSVP to events.
    For O(1) dashboard access without expensive aggregation queries.
    """
    try:
        # Use atomic update with F expressions for thread-safe counter updates
        # Atomically update the participant count using F() expressions, ensuring it doesn't go below 0
        Event.objects.filter(pk=instance.event.pk, participant_count__gt=0).update(
            participant_count=F("participant_count") - 1
        )

        # Update user participation count, ensuring it doesn't go below 0
        UserProfile.objects.filter(
            user=instance.user, participation_count__gt=0
        ).update(participation_count=F("participation_count") - 1)
    except Exception as e:
        # Log error if updating participant counters fails
        import logging

        logger = logging.getLogger(__name__)
        logger.error(
            f"Error updating participant counters for event {instance.event.pk}: {str(e)}"
        )


def _handle_new_event_counters(instance, today):
    """Handle counters for newly created events."""
    # Atomic increments for new event
    if instance.category_id:
        Category.objects.filter(pk=instance.category_id).update(
            event_count=F("event_count") + 1
        )
    if instance.organizer_id:
        UserProfile.objects.get_or_create(user_id=instance.organizer_id)
        UserProfile.objects.filter(user_id=instance.organizer_id).update(
            organized_event_count=F("organized_event_count") + 1
        )

    # Update DashboardStats for today
    DashboardStats.objects.get_or_create(stat_date=today)
    DashboardStats.objects.filter(stat_date=today).update(
        total_events=F("total_events") + 1,
        upcoming_events=F("upcoming_events") + (1 if instance.date >= today else 0),
        past_events=F("past_events") + (1 if instance.date < today else 0),
    )


def _handle_category_drift(instance, old_vals, today):
    """Handle category changes for existing events."""
    old_cat_id = old_vals.get("category_id")
    if old_cat_id != instance.category_id:
        if old_cat_id:
            Category.objects.filter(pk=old_cat_id, event_count__gt=0).update(
                event_count=F("event_count") - 1
            )
        if instance.category_id:
            Category.objects.filter(pk=instance.category_id).update(
                event_count=F("event_count") + 1
            )


def _handle_organizer_drift(instance, old_vals, today):
    """Handle organizer changes for existing events."""
    old_org_id = old_vals.get("organizer_id")
    if old_org_id != instance.organizer_id:
        if old_org_id:
            UserProfile.objects.filter(
                user_id=old_org_id, organized_event_count__gt=0
            ).update(organized_event_count=F("organized_event_count") - 1)
        if instance.organizer_id:
            UserProfile.objects.get_or_create(user_id=instance.organizer_id)
            UserProfile.objects.filter(user_id=instance.organizer_id).update(
                organized_event_count=F("organized_event_count") + 1
            )


def _handle_date_drift(instance, old_vals, today):
    """Handle date changes for existing events in DashboardStats."""
    old_date = old_vals.get("date")
    if old_date and old_date != instance.date:
        DashboardStats.objects.get_or_create(stat_date=today)
        if old_date >= today:  # Was upcoming
            DashboardStats.objects.filter(stat_date=today).update(
                upcoming_events=F("upcoming_events") - 1
            )
        else:  # Was past
            DashboardStats.objects.filter(stat_date=today).update(
                past_events=F("past_events") - 1
            )

        if instance.date >= today:  # Is now upcoming
            DashboardStats.objects.filter(stat_date=today).update(
                upcoming_events=F("upcoming_events") + 1
            )
        else:  # Is now past
            DashboardStats.objects.filter(stat_date=today).update(
                past_events=F("past_events") + 1
            )


@receiver(post_save, sender=Event)
def update_event_counters_on_save(sender, instance, created, **kwargs):
    """
    Updates dashboard counters when events are created or updated.
    Handles category, organizer, and date changes for atomic integrity.
    """
    logger = logging.getLogger(__name__)
    today = timezone.now().date()

    try:
        if created:
            _handle_new_event_counters(instance, today)
        else:
            # Handle updates: detect changed fields using captured _old_values
            old_vals = getattr(instance, "_old_values", {})
            _handle_category_drift(instance, old_vals, today)
            _handle_organizer_drift(instance, old_vals, today)
            _handle_date_drift(instance, old_vals, today)

    except Exception as e:
        logger.error(f"Error in update_event_counters_on_save: {str(e)}")


def _update_category_counter_on_delete(instance):
    """Update category counter when an event is deleted."""
    if instance.category_id:
        Category.objects.filter(pk=instance.category_id, event_count__gt=0).update(
            event_count=F("event_count") - 1
        )


def _update_organizer_counter_on_delete(instance):
    """Update organizer counter when an event is deleted."""
    if instance.organizer_id:
        UserProfile.objects.filter(
            user_id=instance.organizer_id, organized_event_count__gt=0
        ).update(organized_event_count=F("organized_event_count") - 1)


def _update_dashboard_stats_on_delete(instance, today):
    """Update dashboard stats when an event is deleted."""
    DashboardStats.objects.get_or_create(stat_date=today)
    DashboardStats.objects.filter(stat_date=today).update(
        total_events=F("total_events") - 1,
        upcoming_events=F("upcoming_events") - (1 if instance.date >= today else 0),
        past_events=F("past_events") - (1 if instance.date < today else 0),
    )


@receiver(post_delete, sender=Event)
def update_event_counters_on_delete(sender, instance, **kwargs):
    """Updates dashboard counters when events are deleted."""
    logger = logging.getLogger(__name__)
    today = timezone.now().date()

    try:
        _update_category_counter_on_delete(instance)
        _update_organizer_counter_on_delete(instance)
        _update_dashboard_stats_on_delete(instance, today)
    except Exception as e:
        logger.error(f"Error in update_event_counters_on_delete: {str(e)}")
