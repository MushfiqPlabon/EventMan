from allauth.account.forms import SignupForm
from django import forms
from django.core.validators import FileExtensionValidator, MaxValueValidator

from .models import Category, Event


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Last Name"}),
    )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        # Assign the participant role by default
        from django.contrib.auth.models import Group

        participant_group, created = Group.objects.get_or_create(name="Participant")
        user.groups.add(participant_group)

        return user


class EventForm(forms.ModelForm):
    image = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            MaxValueValidator(5 * 1024 * 1024),
        ],  # 5MB max
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
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "required": "required",
                    "maxlength": "200",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "required": "required",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "type": "date",
                    "required": "required",
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "type": "time",
                    "required": "required",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "required": "required",
                    "maxlength": "255",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "required": "required",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-900 dark:text-gray-100 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400",
                    "accept": "image/*",
                    "max": "5242880",  # 5MB in bytes
                }
            ),
        }
        labels = {
            "name": "Event Name",
            "description": "Description",
            "date": "Date",
            "time": "Time",
            "location": "Location",
            "category": "Category",
            "image": "Event Image",
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500",
                    "required": "required",
                    "maxlength": "100",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500"
                }
            ),
        }
        labels = {
            "name": "Category Name",
            "description": "Description",
        }
