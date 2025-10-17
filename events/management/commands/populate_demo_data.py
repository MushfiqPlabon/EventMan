from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Category, Event

User = get_user_model()


class Command(BaseCommand):
    help = "Populates the database with demo data for testing and showcasing."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting demo data population..."))

        # --- Clear existing data (optional, for clean runs) ---
        # self.stdout.write("Clearing existing data...")
        # Event.objects.all().delete()
        # Category.objects.all().delete()
        # User.objects.filter(is_superuser=False).delete()
        # Profile.objects.all().delete()

        # --- Create Users ---
        self.stdout.write("Creating demo users...")

        # Admin User
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Admin User: admin/admin123"))
        else:
            self.stdout.write(self.style.WARNING("Admin User already exists."))

        # Organizer User
        organizer_user, created = User.objects.get_or_create(
            username="organizer",
            defaults={
                "email": "organizer@example.com",
                "first_name": "Event",
                "last_name": "Organizer",
            },
        )
        if created:
            organizer_user.set_password("organizer123")
            organizer_user.save()
            self.stdout.write(
                self.style.SUCCESS("Created Organizer User: organizer/organizer123")
            )
            # Add to Organizer group
            organizer_group, _ = Group.objects.get_or_create(name="Organizer")
            organizer_user.groups.add(organizer_group)
        else:
            self.stdout.write(self.style.WARNING("Organizer User already exists."))

        # Participant User
        participant_user, created = User.objects.get_or_create(
            username="participant",
            defaults={
                "email": "participant@example.com",
                "first_name": "Event",
                "last_name": "Participant",
            },
        )
        if created:
            participant_user.set_password("participant123")
            participant_user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Created Participant User: participant/participant123"
                )
            )
            # Add to Participant group
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            participant_user.groups.add(participant_group)
        else:
            self.stdout.write(self.style.WARNING("Participant User already exists."))

        # --- Create Categories ---
        self.stdout.write("Creating demo categories...")
        category1, _ = Category.objects.get_or_create(name="Conference")
        category2, _ = Category.objects.get_or_create(name="Workshop")
        category3, _ = Category.objects.get_or_create(name="Concert")
        category4, _ = Category.objects.get_or_create(name="Meetup")
        self.stdout.write(self.style.SUCCESS("Demo categories created."))

        # --- Create Events ---
        self.stdout.write("Creating demo events...")
        today = timezone.localdate()

        # Upcoming Event
        event1, _ = Event.objects.get_or_create(
            name="Future Tech Summit",
            defaults={
                "description": "A summit on the future of technology and AI.",
                "date": today + timedelta(days=30),
                "time": "10:00:00",
                "location": "Virtual Event",
                "category": category1,
                "organizer": organizer_user,
                "status": Event.STATUS.published,
            },
        )
        event1.participants.add(participant_user)

        # Past Event
        event2, _ = Event.objects.get_or_create(
            name="DjangoCon 2024",
            defaults={
                "description": "Annual Django developer conference.",
                "date": today - timedelta(days=60),
                "time": "09:00:00",
                "location": "New York, USA",
                "category": category1,
                "organizer": organizer_user,
                "status": Event.STATUS.published,
            },
        )
        event2.participants.add(admin_user, participant_user)

        # Today's Event
        event3, _ = Event.objects.get_or_create(
            name="Daily Standup",
            defaults={
                "description": "Quick team sync-up.",
                "date": today,
                "time": "09:30:00",
                "location": "Online Meeting",
                "category": category4,
                "organizer": organizer_user,
                "status": Event.STATUS.published,
            },
        )

        # Draft Event
        event4, _ = Event.objects.get_or_create(
            name="New Product Launch (Draft)",
            defaults={
                "description": "Internal planning for a new product launch.",
                "date": today + timedelta(days=90),
                "time": "14:00:00",
                "location": "Company HQ",
                "category": category2,
                "organizer": organizer_user,
                "status": Event.STATUS.draft,
            },
        )

        # Cancelled Event
        event5, _ = Event.objects.get_or_create(
            name="Cancelled Music Festival",
            defaults={
                "description": "Due to unforeseen circumstances, this event is cancelled.",
                "date": today + timedelta(days=15),
                "time": "18:00:00",
                "location": "City Park",
                "category": category3,
                "organizer": organizer_user,
                "status": Event.STATUS.cancelled,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo events created."))

        self.stdout.write(self.style.SUCCESS("Demo data population complete!"))
        self.stdout.write("\n--- Demo Credentials ---")
        self.stdout.write("Admin: username=admin, password=admin123")
        self.stdout.write("Organizer: username=organizer, password=organizer123")
        self.stdout.write("Participant: username=participant, password=participant123")
        self.stdout.write("------------------------")
