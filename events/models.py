from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model # Import Django's User model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model() # Get the active User model

# Define a default image path for events
DEFAULT_EVENT_IMAGE = 'event_images/default_event.webp'
DEFAULT_PROFILE_PICTURE = 'profile_pictures/default_profile.webp'

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

class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default=DEFAULT_PROFILE_PICTURE, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()