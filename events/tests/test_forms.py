import pytest

from events.forms.forms import CategoryForm
from events.tests.factories import CategoryFactory


@pytest.mark.django_db
def test_category_form_valid_data():
    form_data = {
        "name": "New Category",
        "description": "A description for the new category.",
    }
    form = CategoryForm(data=form_data)
    assert form.is_valid() is True
    category = form.save()
    assert category.pk is not None
    assert category.name == "New Category"


@pytest.mark.django_db
def test_category_form_invalid_data_missing_name():
    form_data = {"description": "A description without a name."}
    form = CategoryForm(data=form_data)
    assert form.is_valid() is False
    assert "name" in form.errors


@pytest.mark.django_db
def test_category_form_initialization():
    category = CategoryFactory(
        name="Existing Category", description="Existing description"
    )
    form = CategoryForm(instance=category)
    assert form.initial["name"] == "Existing Category"
    assert form.initial["description"] == "Existing description"
