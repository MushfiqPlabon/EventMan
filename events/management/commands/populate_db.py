import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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

# Required admin user data (yours)
REQUIRED_SUPERUSER_DATA = {
    "username": "admin_required",
    "email": "someone@example.com",
    "password": "admin123",
    "first_name": "Required",
    "last_name": "Admin",
}

USER_DATA = [
    # Existing users
    {
        "username": "organizer_jane",
        "email": "jane.doe@example.com",
        "password": "password123",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "Organizer",
    },
    {
        "username": "participant_john",
        "email": "john.smith@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Smith",
        "role": "Participant",
    },
    {
        "username": "participant_emily",
        "email": "emily.jones@example.com",
        "password": "password123",
        "first_name": "Emily",
        "last_name": "Jones",
        "role": "Participant",
    },
    # Required users (yours)
    {
        "username": "organizer1",
        "email": "organizer1@example.com",
        "password": "testpass123",
        "first_name": "Organizer",
        "last_name": "One",
        "role": "Organizer",
    },
    {
        "username": "organizer2",
        "email": "organizer2@example.com",
        "password": "testpass123",
        "first_name": "Organizer",
        "last_name": "Two",
        "role": "Organizer",
    },
    {
        "username": "participant1",
        "email": "participant1@example.com",
        "password": "testpass123",
        "first_name": "Participant",
        "last_name": "One",
        "role": "Participant",
    },
    {
        "username": "participant2",
        "email": "participant2@example.com",
        "password": "testpass123",
        "first_name": "Participant",
        "last_name": "Two",
        "role": "Participant",
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
    {
        "name": "Workshop",
        "description": "Educational and training workshops.",
    },
]

EVENT_DATA = [
    # Existing events
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
    # New events for required users
    {
        "name": "Required Organizer Event",
        "description": "Event created by required organizer.",
        "date": datetime.date(2025, 8, 10),
        "time": datetime.time(14, 0, 0),
        "location": "Required Location",
        "category": "Tech Conference",
        "organizer": "organizer1",
        "participants": ["participant1", "participant2"],
    },
    {
        "name": "Second Required Event",
        "description": "Another event for required users.",
        "date": datetime.date(2025, 9, 20),
        "time": datetime.time(16, 0, 0),
        "location": "Another Location",
        "category": "Workshop",
        "organizer": "organizer2",
        "participants": ["participant1"],
    },
]


class Command(BaseCommand):
    help = "Populates the database with hardcoded, deterministic sample data including required users."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting database population..."))

        # --- 1. Clean up existing data ---
        self.stdout.write("Deleting existing data...")
        Event.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        # Create groups for role-based access ahead of time
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        participant_group, _ = Group.objects.get_or_create(name="Participant")

        # --- 2. Create Superuser ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Superusers ---"))
        # Create existing superuser
        User.objects.create_superuser(**SUPERUSER_DATA)
        self.stdout.write(
            f"  - Existing Superuser: {SUPERUSER_DATA['username']} (email: {SUPERUSER_DATA['email']})"
        )

        # Create required superuser
        User.objects.create_superuser(**REQUIRED_SUPERUSER_DATA)
        self.stdout.write(
            f"  - Required Superuser: {REQUIRED_SUPERUSER_DATA['username']} (email: {REQUIRED_SUPERUSER_DATA['email']})"
        )

        # --- 3. Create Regular Users ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Regular Users ---"))
        users_by_username = {}
        for u_data in USER_DATA:
            user = User.objects.create_user(
                username=u_data["username"],
                email=u_data["email"],
                first_name=u_data["first_name"],
                last_name=u_data["last_name"],
                is_active=True,
            )
            user.set_password(u_data["password"])
            user.save()

            # Assign to appropriate group based on role - O(1) dictionary lookup
            role_group_map = {
                "Organizer": organizer_group,
                "Participant": participant_group
            }

            if u_data["role"] in role_group_map:
                user.groups.add(role_group_map[u_data["role"]])

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

        self.stdout.write(
            self.style.SUCCESS(
                "\nDatabase successfully populated with all required users!"
            )
        )
