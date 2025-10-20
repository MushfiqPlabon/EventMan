import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from events.tests.factories import (CategoryFactory, EventFactory,
                                    PaymentFactory, UserFactory)
from events.views import (get_admin_stats_htmx, get_organizer_stats_htmx,
                          get_participant_payments_htmx)


@pytest.fixture
def admin_user():
    user = UserFactory(is_staff=True, is_superuser=True)
    return user


@pytest.fixture
def organizer_user():
    user = UserFactory()
    organizer_group, _ = Group.objects.get_or_create(name="Organizer")
    user.groups.add(organizer_group)
    return user


@pytest.fixture
def participant_user():
    user = UserFactory()
    participant_group, _ = Group.objects.get_or_create(name="Participant")
    user.groups.add(participant_group)
    return user


@pytest.fixture
def setup_dashboard_data(admin_user, organizer_user, participant_user):
    category = CategoryFactory()
    event1 = EventFactory(
        organizer=organizer_user,
        category=category,
        ticket_price=50.00,
        tickets_sold=10,
        status="published",
    )
    event2 = EventFactory(
        organizer=organizer_user,
        category=category,
        ticket_price=25.00,
        tickets_sold=5,
        status="published",
    )
    event3 = EventFactory(
        organizer=admin_user, category=category, ticket_price=100.00, tickets_sold=2
    )

    PaymentFactory(user=participant_user, event=event1, amount=event1.ticket_price)
    PaymentFactory(user=participant_user, event=event2, amount=event2.ticket_price)
    PaymentFactory(user=organizer_user, event=event3, amount=event3.ticket_price)

    event1.participants.add(participant_user)
    event2.participants.add(participant_user)
    event3.participants.add(organizer_user)

    return {
        "admin": admin_user,
        "organizer": organizer_user,
        "participant": participant_user,
        "event1": event1,
        "event2": event2,
        "event3": event3,
    }


@pytest.mark.django_db
def test_admin_dashboard_view(client, admin_user, setup_dashboard_data):
    client.force_login(admin_user)
    response = client.get(reverse("admin_dashboard"))
    assert response.status_code == 200
    assert "dashboards/admin_dashboard.html" in [t.name for t in response.templates]
    assert response.context["total_events"] == 3
    assert response.context["total_users"] == 3  # admin, organizer, participant
    assert response.context["total_revenue"] == (50 * 10 + 25 * 5 + 100 * 2)
    assert response.context["total_tickets_sold"] == (10 + 5 + 2)
    assert response.context["all_payments"].count() == 3


@pytest.mark.django_db
def test_organizer_dashboard_view(client, organizer_user, setup_dashboard_data):
    client.force_login(organizer_user)
    response = client.get(reverse("organizer_dashboard"))
    assert response.status_code == 200
    assert "dashboards/organizer_dashboard.html" in [t.name for t in response.templates]
    assert response.context["total_events"] == 2  # event1 and event2 by organizer_user
    assert response.context["total_revenue"] == (50 * 10 + 25 * 5)
    assert response.context["total_tickets_sold"] == (10 + 5)


@pytest.mark.django_db
def test_participant_dashboard_view(client, participant_user, setup_dashboard_data):
    client.force_login(participant_user)
    response = client.get(reverse("participant_dashboard"))
    assert response.status_code == 200
    assert "dashboards/participant_dashboard.html" in [
        t.name for t in response.templates
    ]
    assert response.context["my_events"].count() == 2  # event1 and event2


# HTMX endpoint tests


@pytest.mark.django_db
def test_get_admin_stats_htmx(client, admin_user, setup_dashboard_data):
    client.force_login(admin_user)
    response = client.get(reverse(get_admin_stats_htmx))
    assert response.status_code == 200
    assert "events/_admin_stats.html" in [t.name for t in response.templates]
    assert b"Total Revenue" in response.content


@pytest.mark.django_db
def test_get_organizer_stats_htmx(client, organizer_user, setup_dashboard_data):
    client.force_login(organizer_user)
    response = client.get(reverse(get_organizer_stats_htmx))
    assert response.status_code == 200
    assert "events/_organizer_stats.html" in [t.name for t in response.templates]
    assert b"Total Revenue" in response.content


@pytest.mark.django_db
def test_get_participant_payments_htmx(client, participant_user, setup_dashboard_data):
    client.force_login(participant_user)
    response = client.get(reverse(get_participant_payments_htmx))
    assert response.status_code == 200
    assert "events/_participant_payments.html" in [t.name for t in response.templates]
    assert b"Transaction ID" in response.content
