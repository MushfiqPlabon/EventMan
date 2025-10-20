import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_view_status_code(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_view_template(client):
    response = client.get(reverse("home"))
    assert "home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_view_context_data(client):
    response = client.get(reverse("home"))
    assert "featured_events" in response.context
    assert "total_events" in response.context
    assert "total_categories" in response.context
