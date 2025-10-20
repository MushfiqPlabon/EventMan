import factory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from events.models import Category, Event, Payment, Profile

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_staff = False
    is_active = True
    password = factory.django.Password("password123")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker("paragraph", nb_sentences=2)


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph", nb_sentences=5)

    # Use FuzzyDate and FuzzyTime for realistic date and time ranges
    date = factory.Faker("date_this_month")
    time = factory.Faker("time_object")

    location = factory.Faker("address")
    category = factory.SubFactory(CategoryFactory)
    organizer = factory.SubFactory(UserFactory)
    ticket_price = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=0,
        max_value=500,
    )
    tickets_sold = factory.Faker("random_int", min=0, max=100)
    status = factory.Iterator([choice[0] for choice in Event.STATUS])

    # For image fields, you might need to create a dummy file or mock Cloudinary
    # For now, we'll leave it blank or provide a simple path if the model allows
    # If the model requires a file, you'd typically use a temporary file or mock
    image = factory.LazyAttribute(
        lambda o: ContentFile(
            b"dummy_image_content", name=f'{o.name.replace(" ", "_")}.jpg'
        )
    )


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    amount = factory.LazyAttribute(
        lambda o: o.event.ticket_price
    )  # Amount matches event ticket price
    transaction_id = factory.Sequence(lambda n: f"txn_{n:08d}")
    status = factory.Iterator(
        [choice[0] for choice in Payment._meta.get_field("status").choices]
    )


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker("phone_number")
    bio = factory.Faker("paragraph", nb_sentences=3)
    # Similar to Event image, handle profile_picture
    profile_picture = factory.LazyAttribute(
        lambda o: ContentFile(
            b"dummy_profile_content", name=f"{o.user.username}_profile.jpg"
        )
    )
