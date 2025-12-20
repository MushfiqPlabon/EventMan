import datetime

# Import EmailAddress model to create verification records for demo users
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from events.models import Category, Event, EventParticipant

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
        "name": "DjangoCon 2026",
        "description": "The annual conference for the Django web framework.",
        "date": datetime.date(2026, 9, 15),
        "time": datetime.time(9, 0, 0),
        "location": "San Diego, CA",
        "category": "Tech Conference",
        "organizer": "organizer_jane",
        "participants": ["participant_john", "participant_emily"],
    },
    {
        "name": "Summer Fest",
        "description": "An outdoor music festival with multiple stages.",
        "date": datetime.date(2026, 7, 20),
        "time": datetime.time(12, 0, 0),
        "location": "Golden Gate Park, SF",
        "category": "Music Festival",
        "organizer": "organizer_jane",
        "participants": ["participant_emily"],
    },
    {
        "name": "Local Python Meetup",
        "description": "Monthly meetup for Python enthusiasts.",
        "date": datetime.date(2026, 11, 30),
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
        "date": datetime.date(2026, 8, 10),
        "time": datetime.time(14, 0, 0),
        "location": "Required Location",
        "category": "Tech Conference",
        "organizer": "organizer1",
        "participants": ["participant1", "participant2"],
    },
    {
        "name": "Second Required Event",
        "description": "Another event for required users.",
        "date": datetime.date(2026, 9, 20),
        "time": datetime.time(16, 0, 0),
        "location": "Another Location",
        "category": "Workshop",
        "organizer": "organizer2",
        "participants": ["participant1"],
    },
]


class Command(BaseCommand):
    help = "Populates the database with hardcoded, deterministic sample data including required users."

    def _clean_existing_data(self):
        """Clean up existing data before population."""
        Event.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

    def _create_groups(self):
        """Create groups for role-based access."""
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        participant_group, _ = Group.objects.get_or_create(name="Participant")
        return organizer_group, participant_group

    def _create_superuser(self, superuser_data, group=None):
        """Create a superuser with email verification."""
        user = User.objects.create_superuser(**superuser_data)
        EmailAddress.objects.create(
            user=user,
            email=superuser_data["email"],
            verified=True,  # Mark as verified since these are demo accounts
            primary=True,
        )
        self.stdout.write(
            f"  - Superuser: {superuser_data['username']} (email: {superuser_data['email']})"
        )
        return user

    def _create_regular_user(self, user_data, organizer_group, participant_group):
        """Create a regular user with appropriate group assignment."""
        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=True,
        )
        user.set_password(user_data["password"])
        user.save()

        # Create email address verification record for demo users
        EmailAddress.objects.create(
            user=user,
            email=user_data["email"],
            verified=True,  # Mark as verified since these are demo accounts
            primary=True,
        )

        # Assign to appropriate group based on role - O(1) dictionary lookup
        role_group_map = {
            "Organizer": organizer_group,
            "Participant": participant_group,
        }

        if user_data["role"] in role_group_map:
            user.groups.add(role_group_map[user_data["role"]])

        self.stdout.write(
            f"  - User: {user_data['username']} (password: {user_data['password']})"
        )
        return user

    def _create_categories(self):
        """Create categories from the data."""
        categories_by_name = {}
        for c_data in CATEGORY_DATA:
            category = Category.objects.create(**c_data)
            categories_by_name[category.name] = category
            self.stdout.write(f"  - Category: {category.name}")
        return categories_by_name

    def _create_events(self, users_by_username, categories_by_name):
        """Create events from the data."""
        for event_info in EVENT_DATA:
            # Use a copy to avoid modifying the global EVENT_DATA
            e_data = event_info.copy()

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

            # Create EventParticipant records individually so signals fire
            for username in participant_usernames:
                participant = users_by_username[username]
                EventParticipant.objects.create(event=event, user=participant)

            self.stdout.write(f"  - Event: {event.name}")

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting database population..."))

        # --- 1. Clean up existing data ---
        self.stdout.write("Deleting existing data...")
        self._clean_existing_data()

        # Create groups for role-based access ahead of time
        organizer_group, participant_group = self._create_groups()

        # --- 2. Create Superusers ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Superusers ---"))
        self._create_superuser(SUPERUSER_DATA)
        self._create_superuser(REQUIRED_SUPERUSER_DATA)

        # --- 3. Create Regular Users ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Regular Users ---"))
        users_by_username = {}
        for u_data in USER_DATA:
            user = self._create_regular_user(u_data, organizer_group, participant_group)
            users_by_username[user.username] = user

        # --- 4. Create Categories ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Categories ---"))
        categories_by_name = self._create_categories()

        # --- 5. Create Events ---
        self.stdout.write(self.style.SUCCESS("\n--- Creating Events ---"))
        self._create_events(users_by_username, categories_by_name)

        self.stdout.write(
            self.style.SUCCESS(
                "\nDatabase successfully populated with all required users!"
            )
        )
