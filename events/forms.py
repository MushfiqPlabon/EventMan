from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator

from .models import Category, Event

# Constants for form widget CSS classes to reduce repetition
COMMON_INPUT_CLASSES = "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 bg-white leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-700 dark:text-gray-200 dark:border-gray-500"
FILE_INPUT_CLASSES = "block w-full text-sm text-gray-900 dark:text-gray-200 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"


def _validate_name_characters(name_value):
    """Validate that name contains only allowed characters."""
    import re

    if not re.match(r"^[\w\s\-\u00C0-\u017F\u4e00-\u9fff]+$", name_value):
        return False
    return True


def _validate_name_length(name_value, min_length, field_name):
    """Validate that name meets minimum length requirement."""
    if name_value and len(name_value.strip()) < min_length:
        raise forms.ValidationError(
            f"{field_name} must be at least {min_length} characters long."
        )
    return True


def _validate_name_field(name_value, min_length, field_name):
    """Validate a name field with both length and character validation."""
    if not name_value:
        return name_value

    # Validate length
    _validate_name_length(name_value, min_length, field_name)

    # Validate characters if it contains non-alphanumeric characters
    if not name_value.replace(" ", "").replace("-", "").replace("_", "").isalnum():
        if not _validate_name_characters(name_value):
            raise forms.ValidationError(
                f"{field_name} can only contain letters, numbers, spaces, hyphens, underscores, and international characters."
            )

    return name_value


class BaseModelForm(forms.ModelForm):
    """Enhanced base form class with common validation and functionality."""

    def clean_name(self):
        """Common validation for name fields."""
        name = self.cleaned_data.get("name")
        return _validate_name_field(name, 2, "Name")

    def clean_title(self):
        """Alternative name validation for fields named 'title'."""
        title = self.cleaned_data.get("title")
        return _validate_name_field(title, 2, "Title")

    def clean_description(self):
        """Common validation for description fields."""
        description = self.cleaned_data.get("description")
        if description and len(description.strip()) < 5:
            raise forms.ValidationError(
                "Description must be at least 5 characters long."
            )
        return description


class CustomSignupForm(SignupForm):
    username = forms.CharField(max_length=150, label="Username")
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    def __init__(self, *args, **kwargs):
        # Call parent init first
        super(CustomSignupForm, self).__init__(*args, **kwargs)

        # Override the password fields with our styling
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={
                "class": COMMON_INPUT_CLASSES,
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        )

        self.fields["password2"].widget = forms.PasswordInput(
            attrs={
                "class": COMMON_INPUT_CLASSES,
                "placeholder": "Confirm Password",
                "autocomplete": "new-password",
            }
        )

        # Also update email fields to ensure they have proper styling
        self.fields["email"].widget.attrs.update(
            {"class": COMMON_INPUT_CLASSES, "placeholder": "Email"}
        )

        if "email2" in self.fields:
            self.fields["email2"].widget.attrs.update(
                {"class": COMMON_INPUT_CLASSES, "placeholder": "Confirm Email"}
            )

        # Update first_name and last_name if they exist
        if "username" in self.fields:
            self.fields["username"].widget.attrs.update(
                {"class": COMMON_INPUT_CLASSES, "placeholder": "Username"}
            )
        if "first_name" in self.fields:
            self.fields["first_name"].widget.attrs.update(
                {"class": COMMON_INPUT_CLASSES, "placeholder": "First Name"}
            )
        if "last_name" in self.fields:
            self.fields["last_name"].widget.attrs.update(
                {"class": COMMON_INPUT_CLASSES, "placeholder": "Last Name"}
            )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        # Set additional fields
        user.username = self.cleaned_data.get("username", user.username)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        # Assign the participant role by default
        from django.contrib.auth.models import Group

        participant_group, _ = Group.objects.get_or_create(name="Participant")
        user.groups.add(participant_group)

        return user

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username or len(username.strip()) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name and not first_name.replace(" ", "").isalpha():
            raise forms.ValidationError(
                "First name should only contain letters and spaces"
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name and not last_name.replace(" ", "").isalpha():
            raise forms.ValidationError(
                "Last name should only contain letters and spaces"
            )
        return last_name


class EventForm(BaseModelForm):
    image = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            MaxValueValidator(settings.EVENT_IMAGE_MAX_SIZE),
        ],  # Configurable image size limit
        required=False,
    )

    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "date",
            "time",
            "location",
            "category",
            "image",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "required": "required",
                    "maxlength": "200",
                    "placeholder": "Enter event name",
                    "title": "Event name is required and must be unique",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "required": "required",
                    "placeholder": "Describe the event",
                    "rows": 4,
                    "title": "Event description is required",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "type": "date",
                    "required": "required",
                    "title": "Event date is required and must be in the future",
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "type": "time",
                    "required": "required",
                    "title": "Event time is required",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "required": "required",
                    "maxlength": "255",
                    "placeholder": "Enter event location",
                    "title": "Event location is required",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "required": "required",
                    "title": "Please select a category for the event",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": FILE_INPUT_CLASSES,
                    "accept": "image/*",
                    "max": "5242880",  # 5MB in bytes
                }
            ),
        }
        labels = {
            "name": "Event Name *",
            "description": "Description *",
            "date": "Date *",
            "time": "Time *",
            "location": "Location *",
            "category": "Category *",
            "image": "Event Image",
        }

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date and date < self.get_today():
            raise forms.ValidationError("The event date cannot be in the past.")
        return date

    def clean_name(self):
        name = super().clean_name()  # Call parent validation first for basic checks
        # Additional validation specific to Event name (3 chars minimum vs 2 in parent)
        if name and len(name.strip()) < 3:
            raise forms.ValidationError(
                "Event name must be at least 3 characters long."
            )
        return name

    def clean_description(self):
        description = (
            super().clean_description()
        )  # Call parent validation first for basic checks
        if description and len(description.strip()) < 10:
            raise forms.ValidationError(
                "Event description must be at least 10 characters long."
            )
        return description

    def get_today(self):
        """Helper method to allow testing with different dates."""
        from django.utils import timezone

        return timezone.now().date()


class CategoryForm(BaseModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "required": "required",
                    "maxlength": "100",
                    "placeholder": "Enter category name",
                    "title": "Category name is required and must be unique",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": COMMON_INPUT_CLASSES,
                    "placeholder": "Describe the category",
                    "rows": 3,
                    "title": "Category description (optional)",
                }
            ),
        }
        labels = {
            "name": "Category Name *",
            "description": "Description",
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and len(name.strip()) < 2:
            raise forms.ValidationError(
                "Category name must be at least 2 characters long."
            )
        return name


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        # Apply the common input classes to the login fields
        self.fields["login"].widget.attrs.update(
            {"class": COMMON_INPUT_CLASSES, "placeholder": "Email or Username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": COMMON_INPUT_CLASSES, "placeholder": "Password"}
        )
