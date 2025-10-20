import pytest

from events.models import Category
from events.tests.factories import CategoryFactory


@pytest.mark.django_db
def test_category_creation():
    category = CategoryFactory()
    assert category.pk is not None
    assert isinstance(category, Category)
    assert Category.objects.count() == 1


@pytest.mark.django_db
def test_category_str_representation():
    category = CategoryFactory(name="Test Category")
    assert str(category) == "Test Category"


@pytest.mark.django_db
def test_category_unique_name_constraint():
    CategoryFactory(name="Unique Category")
    with pytest.raises(Exception):  # Expecting IntegrityError or similar from DB
        CategoryFactory(name="Unique Category")
