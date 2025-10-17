from django.core.mail import send_mail
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Event  # Import your Event model


@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_email_notification(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """
    Sends an email notification when a user RSVPs to an event.
    Triggered by m2m_changed signal on Event.participants.
    """
    if action == "post_add":  # User has been added to participants
        for user_pk in pk_set:
            user = model.objects.get(pk=user_pk)
            event = instance  # The event instance
            subject = f"RSVP Confirmation for: {event.name}"
            html_message = render_to_string(
                "emails/rsvp_confirmation.html", {"user": user, "event": event}
            )
            plain_message = strip_tags(html_message)
            from_email = "noreply@yourdomain.com"  # Replace with your actual email
            to_email = [user.email]

            send_mail(
                subject, plain_message, from_email, to_email, html_message=html_message
            )
            print(
                f"RSVP Confirmation email sent to {user.email} for event {event.name}"
            )  # For console output in development
    # You could add 'post_remove' logic here for un-RSVP notifications if needed
