import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from events.models import Category, Event

User = get_user_model()

# --- Hardcoded Data Definition ---

SUPERUSER_DATA = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "adminpassword",
    "first_name": "Admin",
    "last_name": "User",
}

USER_DATA = [
    {
        "username": "organizer_jane",
        "email": "jane.doe@example.com",
        "password": "password123",
        "first_name": "Jane",
        "last_name": "Doe",
    },
    {
        "username": "participant_john",
        "email": "john.smith@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Smith",
    },
    {
        "username": "participant_emily",
        "email": "emily.jones@example.com",
        "password": "password123",
        "first_name": "Emily",
        "last_name": "Jones",
    },
]

CATEGORY_DATA = [
    {
        "name": "Tech Conference",
        "description": "Events focused on software development, AI, and other technologies.",
    },
    {
        "name": "Music Festival",
        "description": "Live music events spanning various genres.",
    },
    {
        "name": "Community Meetup",
        "description": "Local community gatherings and social events.",
    },
]

EVENT_DATA = [
    {
        "name": "DjangoCon 2025",
        "description": "The annual conference for the Django web framework.",
        "date": datetime.date(2025, 9, 15),
        "time": datetime.time(9, 0, 0),
        "location": "San Diego, CA",
        "category": "Tech Conference",
        "organizer": "organizer_jane",
        "participants": ["participant_john", "participant_emily"],
    },
    {
        "name": "Summer Fest",
        "description": "An outdoor music festival with multiple stages.",
        "date": datetime.date(2025, 7, 20),
        "time": datetime.time(12, 0, 0),
        "location": "Golden Gate Park, SF",
        "category": "Music Festival",
        "organizer": "organizer_jane",
        "participants": ["participant_emily"],
    },
    {
        "name": "Local Python Meetup",
        "description": "Monthly meetup for Python enthusiasts.",
        "date": datetime.date(2025, 11, 30),
        "time": datetime.time(19, 0, 0),
        "location": "123 Main St, Anytown, USA",
        "category": "Community Meetup",
        "organizer": "organizer_jane",
        "participants": ["participant_john"],
    },
]


class Command(BaseCommand):
    help = "Populates the database with hardcoded, deterministic sample data."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting database population..."))

        # --- 1. Clean up existing data ---
        self.stdout.write("Deleting existing data...")
        Event.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        # --- 2. Create Superuser ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Superuser ---"))
        User.objects.create_superuser(**SUPERUSER_DATA)
        self.stdout.write(
            f"  - Superuser: {SUPERUSER_DATA['username']} (password: {SUPERUSER_DATA['password']})"
        )

        # --- 3. Create Regular Users ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Regular Users ---"))
        users_by_username = {}
        for u_data in USER_DATA:
            user = User.objects.create_user(**u_data)
            users_by_username[user.username] = user
            self.stdout.write(
                f"  - User: {u_data['username']} (password: {u_data['password']})"
            )

        # --- 4. Create Categories ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Categories ---"))
        categories_by_name = {}
        for c_data in CATEGORY_DATA:
            category = Category.objects.create(**c_data)
            categories_by_name[category.name] = category
            self.stdout.write(f"  - Category: {category.name}")

        # --- 5. Create Events ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Events ---"))
        for e_data in EVENT_DATA:
            # Pop relationship keys from the data dictionary to avoid multiple values error
            organizer_username = e_data.pop("organizer")
            category_name = e_data.pop("category")
            participant_usernames = e_data.pop("participants")

            # O(1) lookup from in-memory dictionaries
            organizer = users_by_username[organizer_username]
            category = categories_by_name[category_name]

            event = Event.objects.create(
                organizer=organizer, category=category, **e_data
            )

            # O(1) lookups for participants
            participant_objects = [
                users_by_username[username] for username in participant_usernames
            ]
            event.participants.set(participant_objects)

            self.stdout.write(f"  - Event: {e_data['name']}")

        self.stdout.write(self.style.SUCCESS("\nDatabase successfully populated!"))
