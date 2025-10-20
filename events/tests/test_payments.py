import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from events.models import Payment
from events.tests.factories import CategoryFactory, EventFactory, UserFactory

User = get_user_model()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def category():
    return CategoryFactory()


@pytest.fixture
def event(user, category):
    return EventFactory(
        organizer=user, category=category, ticket_price=100.00, tickets_sold=0
    )


@pytest.fixture
def sslcommerz_mock(mocker):
    mock_sslcz = mocker.patch("events.views.SSLCOMMERZ").return_value
    mock_sslcz.createSession.return_value = {
        "status": "SUCCESS",
        "GatewayPageURL": "https://sandbox.sslcommerz.com/gwprocess/v4/url.php?am=123",
    }
    mock_sslcz.validationResponse.return_value = True
    return mock_sslcz


@pytest.fixture
def config_mock(mocker):
    mock_config = mocker.patch("events.views.config")
    mock_config.side_effect = lambda key, default=None, cast=None: {
        "SSLCOMMERZ_STORE_ID": "test_store_id",
        "SSLCOMMERZ_STORE_PASS": "test_store_pass",
        "SSLCOMMERZ_IS_SANDBOX": True,
    }.get(key, default)
    return mock_config


@pytest.mark.django_db
def test_initiate_payment_authenticated_success(
    client, user, event, sslcommerz_mock, config_mock
):
    client.force_login(user)
    sslcommerz_mock.createSession.return_value = {
        "status": "SUCCESS",
        "GatewayPageURL": "https://sandbox.sslcommerz.com/gwprocess/v4/url.php?am=123",
    response = client.post(reverse("initiate_payment", kwargs={"pk": event.pk}))

    payment = Payment.objects.first()
    assert payment.status == "Failed"
    assert response.status_code == 302
    assert response.url == reverse("event_detail", kwargs={"pk": event.pk})

    assert Payment.objects.count() == 1
    payment = Payment.objects.first()
    assert payment.user == user
    assert payment.event == event
    assert payment.amount == event.ticket_price
    assert payment.status == "Pending"

    sslcommerz_mock.createSession.assert_called_once()
    assert response.status_code == 302  # Redirect
    assert response.url == "https://sandbox.sslcommerz.com/gwprocess/v4/url.php?am=123"


    @pytest.mark.django_db
def test_initiate_payment_unauthenticated(client, event):
    response = client.post(reverse("initiate_payment", kwargs={"pk": event.pk}))
    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_payment_success_valid(client, user, event, sslcommerz_mock, config_mock):
    payment = Payment.objects.create(
        user=user,
        event=event,
        amount=event.ticket_price,
        status="Pending",
        transaction_id="test_tran_id",
    )
    initial_tickets_sold = event.tickets_sold

    response = client.post(
        reverse("payment_success"), {"tran_id": payment.transaction_id}
    )

    payment.refresh_from_db()
    event.refresh_from_db()

    assert payment.status == "Valid"
    assert event.tickets_sold == initial_tickets_sold + 1
    assert user in event.participants.all()
    assert response.status_code == 200
    assert "payment_success.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_payment_success_invalid_validation(
    client, user, event, sslcommerz_mock, config_mock
):
    payment = Payment.objects.create(
        user=user,
        event=event,
        amount=event.ticket_price,
        status="Pending",
        transaction_id="test_tran_id",
    )
    sslcommerz_mock.validationResponse.return_value = False

    response = client.post(
        reverse("payment_success"), {"tran_id": payment.transaction_id}
    )

    payment.refresh_from_db()
    event.refresh_from_db()

    assert payment.status == "Pending"  # Should not change
    assert event.tickets_sold == 0  # Should not increment
    assert user not in event.participants.all()
    assert response.status_code == 302
    assert response.url == reverse("event_list")


@pytest.mark.django_db
def test_payment_fail(client, user, event, config_mock):
    payment = Payment.objects.create(
        user=user,
        event=event,
        amount=event.ticket_price,
        status="Pending",
        transaction_id="test_tran_id",
    )

    response = client.post(reverse("payment_fail"), {"tran_id": payment.transaction_id})

    payment.refresh_from_db()
    assert payment.status == "Failed"
    assert response.status_code == 200
    assert "payment_fail.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_payment_ipn_valid(client, user, event, sslcommerz_mock, config_mock):
    payment = Payment.objects.create(
        user=user,
        event=event,
        amount=event.ticket_price,
        status="Pending",
        transaction_id="test_tran_id",
    )
    initial_tickets_sold = event.tickets_sold

    response = client.post(reverse("payment_ipn"), {"tran_id": payment.transaction_id})

    payment.refresh_from_db()
    event.refresh_from_db()

    assert payment.status == "Valid"
    assert event.tickets_sold == initial_tickets_sold + 1
    assert user in event.participants.all()
    assert response.status_code == 200
    assert response.content.decode() == "IPN Processed"


@pytest.mark.django_db
def test_payment_ipn_invalid(client, user, event, sslcommerz_mock, config_mock):
    payment = Payment.objects.create(
        user=user,
        event=event,
        amount=event.ticket_price,
        status="Pending",
        transaction_id="test_tran_id",
    )
    sslcommerz_mock.validationResponse.return_value = False

    response = client.post(reverse("payment_ipn"), {"tran_id": payment.transaction_id})

    payment.refresh_from_db()
    event.refresh_from_db()

    assert payment.status == "Pending"  # Should not change
    assert event.tickets_sold == 0  # Should not increment
    assert user not in event.participants.all()
    assert response.status_code == 200
    assert response.content.decode() == "IPN Received"
