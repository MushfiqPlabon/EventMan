# events/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        verbose_name_plural = "Categories"

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

    def __str__(self):
        return f"{self.name} on {self.date}"

    class Meta:
        ordering = ['date', 'time'] # Default ordering for events

class Participant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Participant Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    events = models.ManyToManyField(Event, related_name='participants', blank=True, verbose_name="Events Attending")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] # Default ordering for participants