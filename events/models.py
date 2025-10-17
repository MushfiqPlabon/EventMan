from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

User = get_user_model()

# Define default image paths
DEFAULT_EVENT_IMAGE = "event_images/default_event.webp"
DEFAULT_PROFILE_PICTURE = "profile_pictures/default_profile.webp"


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
    image = models.ImageField(upload_to="event_images/", default=DEFAULT_EVENT_IMAGE)
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


class Profile(TimeStampedModel):
    """User profile with auto timestamps"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default=DEFAULT_PROFILE_PICTURE,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self):
        return f"{self.user.username} Profile"


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
