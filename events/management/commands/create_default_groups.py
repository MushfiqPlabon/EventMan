from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default groups and their permissions"

    def handle(self, *args, **options):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name="Admin")
        organizer_group, created = Group.objects.get_or_create(name="Organizer")
        participant_group, created = Group.objects.get_or_create(name="Participant")

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created groups: Admin, Organizer, Participant"
            )
        )
