import pytest
from django.contrib.auth import get_user_model

from events.models import Profile
from events.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_create_user_profile_signal():
    user = UserFactory()
    assert Profile.objects.count() == 1
    assert hasattr(user, "profile")
    assert user.profile.user == user


@pytest.mark.django_db
def test_save_user_profile_signal():
    user = UserFactory()
    profile = user.profile
    profile.bio
    profile.bio = "Updated bio content"
    profile.save()

    # Reload user to ensure profile is re-fetched
    user.refresh_from_db()
    assert user.profile.bio == "Updated bio content"

    # Test that saving the user also saves the profile
    user.first_name = "NewFirstName"
    user.save()
    profile.refresh_from_db()
    assert user.profile.bio == "Updated bio content"
