from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from .constants import PAYMENT_STATUS_CHOICES, RSVP_STATUS_CHOICES

User = get_user_model()


class Category(TimeStampedModel):
    """Event category with auto timestamps"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(TimeStampedModel, StatusModel):
    """Enhanced Event model with timestamps and status"""

    STATUS = Choices(
        ("draft", "Draft"),
        ("published", "Published"),
        ("cancelled", "Cancelled"),
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(upload_to="event_images/")
    participants = models.ManyToManyField(
        User, related_name="events_joined", blank=True
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
    )
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tickets_sold = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["date", "time"]
        indexes = [
            models.Index(fields=["date", "status"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return self.name

    def is_upcoming(self):
        """Checks if the event date is in the future."""
        return (
            self.date >= timezone.localdate() and self.status == self.STATUS.published
        )

    def is_past(self):
        """Checks if the event date is in the past."""
        return self.date < timezone.localdate()

    def is_today(self):
        """Checks if the event is today."""
        return self.date == timezone.localdate()

    def participant_count(self):
        """Get participant count efficiently."""
        return self.participants.count()


class Payment(TimeStampedModel):
    """Payment model to store transaction details"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Payment {self.transaction_id} for {self.event.name}"


class Profile(TimeStampedModel):
    """User profile with auto timestamps"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self):
        return f"{self.user.username} Profile"


class RSVP(TimeStampedModel):
    """RSVP model to track user attendance for events"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rsvps")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    status = models.CharField(
        max_length=20,
        choices=RSVP_STATUS_CHOICES,
        default="attending",
    )

    class Meta:
        unique_together = ["user", "event"]
        ordering = ["-created"]
        verbose_name = "RSVP"
        verbose_name_plural = "RSVPs"

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.status})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when user is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save profile when user is saved."""
    if hasattr(instance, "profile") and not kwargs.get("raw", False):
        instance.profile.save()
