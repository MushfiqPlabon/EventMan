from decimal import Decimal
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core.files.storage import Storage
from django.core.management import call_command

from events.models import Category, Event, Payment, Profile

User = get_user_model()


@pytest.mark.django_db
def test_populate_demo_data_command(mocker):
    # Mock requests.get to prevent actual image downloads
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.content = b"dummy_image_content"
    mocker.patch("requests.get", return_value=mock_response)

    # Mock ImageField.save to prevent actual file system operations
    mocker.patch.object(Storage, "save", return_value="mock_file_path.jpg")

    call_command("populate_demo_data")

    # Assertions for Users
    assert User.objects.count() == 6
    assert User.objects.filter(username="admin", is_superuser=True).exists()
    assert User.objects.filter(username="organizer").exists()
    assert User.objects.filter(username="participant").exists()

    # Assertions for Profiles (should be created automatically for each user)
    assert Profile.objects.count() == 6

    # Assertions for Categories
    assert Category.objects.count() == 5
    assert Category.objects.filter(name="Conference").exists()

    # Assertions for Events
    assert Event.objects.count() == 5
    future_tech_summit = Event.objects.get(name="Future Tech Summit")
    assert future_tech_summit.ticket_price == Decimal("99.99")
    assert future_tech_summit.participants.count() == 2

    # Assertions for Payments
    assert Payment.objects.count() == 7  # Based on the command's logic
    assert Payment.objects.filter(event__name="Future Tech Summit").count() == 2
    assert Payment.objects.filter(event__name="DjangoCon 2024").count() == 3
