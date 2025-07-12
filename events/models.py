# events/models.py
from django.db import models
from django.conf import settings # Imported settings to reference AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        verbose_name_plural = "Categories" # Correct pluralization for admin

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name="Event Name")
    description = models.TextField(verbose_name="Description")
    date = models.DateField(verbose_name="Event Date")
    time = models.TimeField(verbose_name="Event Time")
    location = models.CharField(max_length=255, verbose_name="Location")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name="Category"
    )
    # New ImageField for Event model
    image = models.ImageField(
        upload_to='event_images/', # Files will be uploaded to MEDIA_ROOT/event_images/
        default='event_images/default_event_image.jpg', # Path to a default image
        blank=True, # Allow empty, but default will be used
        null=True,  # Allow NULL in database
        verbose_name="Event Image"
    )

    # ManyToManyField for RSVP system - links to the User model
    # related_name='rsvped_events' allows accessing events a user has RSVP'd to: user_instance.rsvped_events.all()
    rsvped_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, # Reference the configured User model
        related_name='rsvped_events',
        blank=True, # RSVPs are optional
        verbose_name="RSVP'd Participants"
    )

    def __str__(self):
        return f"{self.name} on {self.date}"

    class Meta:
        ordering = ['date', 'time'] # Default ordering for events
        verbose_name_plural = "Events"