# Import the setting
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


def validate_future_date(value):
    """Validate that the date is not in the past - O(1) operation."""
    if value < timezone.now().date():
        raise ValidationError('Event date cannot be in the past.')


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    date = models.DateField(db_index=True, validators=[validate_future_date])
    time = models.TimeField()
    location = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    image = models.ImageField(
        upload_to="event_images/", default=settings.EVENT_DEFAULT_IMAGE
    )
    participants = models.ManyToManyField(
        User, related_name="events_joined", blank=True
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
        db_index=True,
    )

    def __str__(self):
        return self.name

    def clean(self):
        """Additional validation to prevent past dates - O(1) operation."""
        if self.date and self.date < timezone.now().date():
            raise ValidationError('Event date cannot be in the past.')
        super().clean()

    def save(self, *args, **kwargs):
        """Override save method to run validation - O(1) operation."""
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_upcoming_events(cls):
        """Class method to get upcoming events using queryset."""
        return cls.objects.filter(date__gte=timezone.now().date())

    @classmethod
    def get_past_events(cls):
        """Class method to get past events using queryset."""
        return cls.objects.filter(date__lt=timezone.now().date())
