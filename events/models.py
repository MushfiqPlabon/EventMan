# event_management_system/events/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model # Import Django's User model

User = get_user_model() # Get the active User model

# Define a default image path for events
DEFAULT_EVENT_IMAGE = 'event_images/default_event.webp'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='event_images/', default=DEFAULT_EVENT_IMAGE)
    # New: ManyToMany relationship with the User model for participants
    participants = models.ManyToManyField(User, related_name='events_joined', blank=True)
    # New: Link event to an Organizer (User)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_events')


    def __str__(self):
        return self.name

    def is_upcoming(self):
        """Checks if the event date is in the future."""
        return self.date >= timezone.now().date()

    def is_past(self):
        """Checks if the event date is in the past."""
        return self.date < timezone.now().date()

