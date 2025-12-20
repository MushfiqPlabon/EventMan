# Import the setting
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class DashboardStats(models.Model):
    """
    Materialized view equivalent - stores precalculated dashboard statistics
    for O(1) access instead of expensive aggregation queries.
    """

    stat_date = models.DateField(primary_key=True)  # Date for which stats are valid
    total_events = models.IntegerField(default=0)
    upcoming_events = models.IntegerField(default=0)
    past_events = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard Statistic"
        verbose_name_plural = "Dashboard Statistics"

    def __str__(self):
        return f"Stats for {self.stat_date}"


User = get_user_model()


def validate_future_datetime(date, time):
    """Validate that the date and time combination is not in the past - O(1) operation."""
    # Combine date and time into a datetime object and make it timezone-aware using the current timezone
    if not date or not time:
        return

    event_datetime = timezone.make_aware(
        timezone.datetime.combine(date, time), timezone.get_current_timezone()
    )
    current_time = timezone.now()
    # Add a small buffer to account for timezone differences
    if event_datetime < current_time:
        raise ValidationError("Event date and time cannot be in the past.")


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    # Denormalized count for O(1) access to number of events in this category
    event_count = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class UserProfile(models.Model):
    """Extended user profile with denormalized counts for O(1) access."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Denormalized count for O(1) access to number of events user participates in
    participation_count = models.PositiveIntegerField(default=0, editable=False)
    # Denormalized count for O(1) access to number of events user organizes
    organized_event_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        db_table = "events_userprofile"
        indexes = [
            models.Index(
                fields=["participation_count"]
            ),  # For participant leaderboards/stats
            models.Index(fields=["organized_event_count"]),  # For organizer stats
        ]


class EventManager(models.Manager):
    """Custom manager for optimized Event queries."""

    def with_related_data(self):
        """Return events with common related data."""
        return self.select_related("category", "organizer").only(
            "id",
            "name",
            "description",
            "date",
            "time",
            "location",
            "image",
            "participant_count",
            "category__name",
            "organizer__first_name",
            "organizer__last_name",
        )

    def upcoming(self):
        """Return upcoming events."""
        today = timezone.now().date()
        return self.with_related_data().filter(date__gte=today)

    def past(self):
        """Return past events."""
        today = timezone.now().date()
        return self.with_related_data().filter(date__lt=today)


class EventParticipant(models.Model):
    """Custom through model for Event participants with proper indexing."""

    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")  # Ensures no duplicate RSVPs
        indexes = [
            models.Index(fields=["event", "user"]),  # For checking RSVP status
            models.Index(fields=["user", "event"]),  # For user's event lookups
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"


class Event(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    date = models.DateField(db_index=True)
    time = models.TimeField()
    location = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    image = models.ImageField(
        upload_to="event_images/", default=settings.EVENT_DEFAULT_IMAGE
    )
    participants = models.ManyToManyField(
        User,
        through=EventParticipant,  # Use custom through model with proper indexing
        related_name="events_joined",
        blank=True,
    )
    participant_count = models.PositiveIntegerField(
        default=0, editable=False
    )  # Denormalized count for O(1) access
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
        db_index=True,
    )

    objects = EventManager()

    def __str__(self):
        return self.name

    def clean(self):
        """Override clean method to add custom validation."""
        super().clean()
        if self.date and self.time:
            validate_future_datetime(self.date, self.time)

    def save(self, *args, **kwargs):
        """Override save method to run validation - O(1) operation."""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            # Multi-column indexes for common query patterns
            models.Index(fields=["date", "category"]),
            models.Index(fields=["organizer", "date"]),
            models.Index(fields=["category", "date"]),
            models.Index(fields=["name", "date"]),  # For search + date combination
            models.Index(
                fields=["location", "date"]
            ),  # For location + date combination
            # Additional composite indexes for optimized queries
            models.Index(
                fields=["organizer", "date", "category"]
            ),  # For organizer dashboards with filtering
            models.Index(
                fields=["date", "location", "category"]
            ),  # For complex filtering
            # PostgreSQL-specific indexes for performance
            models.Index(
                fields=["date"], name="event_date_btree_idx"
            ),  # B-tree for date range queries
            # GIN Indexes for O(log n) Full-Text Search (Trigram)
            GinIndex(
                fields=["name"],
                name="event_name_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["location"],
                name="event_location_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["description"],
                name="event_desc_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
            # Partial indexes for common conditions
            models.Index(
                fields=["date", "organizer"],
                condition=models.Q(date__gte=timezone.now().date()),
                name="upcoming_events_partial_idx",
            ),
            # Additional index for organizer dashboard query pattern (today's events for specific organizer)
            models.Index(fields=["organizer", "date"], name="event_organizer_date_idx"),
            # Standard B-tree index for primary key/id (PostgreSQL default)
            models.Index(fields=["id"], name="event_id_btree_idx"),
        ]

    @classmethod
    def get_upcoming_events(cls):
        """Class method to get upcoming events using queryset."""
        return cls.objects.filter(date__gte=timezone.now().date())

    @classmethod
    def get_past_events(cls):
        """Class method to get past events using queryset."""
        return cls.objects.filter(date__lt=timezone.now().date())
