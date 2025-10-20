from datetime import timedelta

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Category, Event, Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Populates the database with demo data for testing and showcasing."

    def download_image(self, seed, width, height):
        """Downloads an image from picsum.photos and returns it as a ContentFile."""
        url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        self.stdout.write(f"Fetching image from: {url}")
        try:
            response = requests.get(url, stream=True, timeout=10)
            self.stdout.write(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                return ContentFile(response.content)
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to download image. Status: {response.status_code}"
                    )
                )
                return None
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error downloading image: {e}"))
            return None

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting demo data population..."))

        # --- Create Groups ---
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        participant_group, _ = Group.objects.get_or_create(name="Participant")

        # --- Create Users ---
        self.stdout.write("Creating demo users...")

        users_to_create = [
            {
                "username": "admin",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
                "group": None,
            },
            {
                "username": "organizer",
                "password": "organizer123",
                "first_name": "Alice",
                "last_name": "Organizer",
                "email": "alice@example.com",
                "group": organizer_group,
            },
            {
                "username": "organizer2",
                "password": "organizer123",
                "first_name": "Bob",
                "last_name": "Planner",
                "email": "bob@example.com",
                "group": organizer_group,
            },
            {
                "username": "participant",
                "password": "participant123",
                "first_name": "Charlie",
                "last_name": "Attendee",
                "email": "charlie@example.com",
                "group": participant_group,
            },
            {
                "username": "participant2",
                "password": "participant123",
                "first_name": "Diana",
                "last_name": "Guest",
                "email": "diana@example.com",
                "group": participant_group,
            },
            {
                "username": "participant3",
                "password": "participant123",
                "first_name": "Eve",
                "last_name": "Visitor",
                "email": "eve@example.com",
                "group": participant_group,
            },
        ]

        users = {}
        for user_data in users_to_create:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "is_staff": user_data.get("is_staff", False),
                    "is_superuser": user_data.get("is_superuser", False),
                },
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                if user_data["group"]:
                    user.groups.add(user_data["group"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created User: {user_data['username']}/{user_data['password']}"
                    )
                )

            # Ensure profile picture exists
            if (
                not user.profile.profile_picture.name
                or "default_profile.webp" in user.profile.profile_picture.name
            ):
                image_content = self.download_image(user.username, 200, 200)
                if image_content:
                    self.stdout.write(f"Downloading image for {user.username}...")
                    try:
                        user.profile.profile_picture.save(
                            f"{user.username}.jpg", image_content, save=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully saved profile picture for {user.username}."
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error saving profile picture for {user.username}: {e}"
                            )
                        )
                    self.stdout.write(
                        self.style.SUCCESS(f"Saved image for {user.username}.")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not download image for {user.username}."
                        )
                    )

            users[user_data["username"]] = user
            self.stdout.write(
                f"User {user.username} picture name: '{user.profile.profile_picture.name}'"
            )

        # --- Create Categories ---
        self.stdout.write("Creating demo categories...")
        categories = {
            cat: Category.objects.get_or_create(name=cat)[0]
            for cat in ["Conference", "Workshop", "Concert", "Meetup", "Webinar"]
        }
        self.stdout.write(self.style.SUCCESS("Demo categories created."))

        # --- Create Events ---
        self.stdout.write("Creating demo events...")
        today = timezone.localdate()

        events_to_create = [
            {
                "name": "Future Tech Summit",
                "organizer": users["organizer"],
                "category": categories["Conference"],
                "date": today + timedelta(days=30),
                "ticket_price": 99.99,
                "participants": [users["participant"], users["participant2"]],
            },
            {
                "name": "DjangoCon 2024",
                "organizer": users["organizer"],
                "category": categories["Conference"],
                "date": today - timedelta(days=60),
                "ticket_price": 149.00,
                "participants": [
                    users["admin"],
                    users["participant"],
                    users["participant3"],
                ],
            },
            {
                "name": "Live Jazz Night",
                "organizer": users["organizer2"],
                "category": categories["Concert"],
                "date": today + timedelta(days=10),
                "ticket_price": 45.00,
                "participants": [users["participant"], users["participant2"]],
            },
            {
                "name": "Data Science Workshop",
                "organizer": users["organizer2"],
                "category": categories["Workshop"],
                "date": today + timedelta(days=5),
                "ticket_price": 75.50,
                "participants": [],
            },
            {
                "name": "Free Community Meetup",
                "organizer": users["organizer"],
                "category": categories["Meetup"],
                "date": today + timedelta(days=3),
                "ticket_price": 0.00,
                "participants": [
                    users["participant"],
                    users["participant2"],
                    users["participant3"],
                ],
            },
        ]

        events = {}
        for event_data in events_to_create:
            event, created = Event.objects.get_or_create(
                name=event_data["name"],
                defaults={
                    "description": f"A great event: {event_data['name']}.",
                    "date": event_data["date"],
                    "time": "10:00:00",
                    "location": "Virtual Event",
                    "category": event_data["category"],
                    "organizer": event_data["organizer"],
                    "status": Event.STATUS.published,
                    "ticket_price": event_data["ticket_price"],
                },
            )
            if created:
                event.participants.add(*event_data["participants"])

            # Ensure event image exists
            if not event.image.name or "default_event.webp" in event.image.name:
                image_content = self.download_image(event.name, 600, 400)
                if image_content:
                    self.stdout.write(f"Downloading image for {event.name}...")
                    try:
                        event.image.save(
                            f"{event.name.lower().replace(' ', '_')}.jpg",
                            image_content,
                            save=True,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully saved image for {event.name}."
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error saving image for {event.name}: {e}"
                            )
                        )
                    self.stdout.write(
                        self.style.SUCCESS(f"Saved image for {event.name}.")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not download image for {event.name}."
                        )
                    )

            events[event_data["name"]] = event
            self.stdout.write(f"Event {event.name} image name: '{event.image.name}'")
        self.stdout.write(self.style.SUCCESS("Demo events created."))

        # --- Create Payments ---
        self.stdout.write("Creating demo payments...")
        payments_to_create = [
            {"user": users["participant"], "event": events["Future Tech Summit"]},
            {"user": users["participant2"], "event": events["Future Tech Summit"]},
            {"user": users["admin"], "event": events["DjangoCon 2024"]},
            {"user": users["participant"], "event": events["DjangoCon 2024"]},
            {"user": users["participant3"], "event": events["DjangoCon 2024"]},
            {"user": users["participant"], "event": events["Live Jazz Night"]},
            {"user": users["participant2"], "event": events["Live Jazz Night"]},
        ]

        for i, payment_data in enumerate(payments_to_create):
            event = payment_data["event"]
            if event.ticket_price > 0:
                payment, created = Payment.objects.get_or_create(
                    transaction_id=f"demotxn_{i+1:03d}",
                    defaults={
                        "user": payment_data["user"],
                        "event": event,
                        "amount": event.ticket_price,
                        "status": "Valid",
                    },
                )
                if created:
                    event.tickets_sold += 1
                    event.save()
        self.stdout.write(self.style.SUCCESS("Demo payments created."))

        self.stdout.write(self.style.SUCCESS("\nDemo data population complete!"))
        self.stdout.write("--- Demo Credentials ---")
        for user_data in users_to_create:
            self.stdout.write(
                f"{user_data['username']}: password={user_data['password']}"
            )
        self.stdout.write("------------------------")
