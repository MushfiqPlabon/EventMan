from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model

from .models import Category, Event, Profile

User = get_user_model()


class EventForm(forms.ModelForm):
    """Enhanced Event form with crispy styling"""

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
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "needs-validation"
        self.helper.attrs = {"novalidate": True}

        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-8 mb-3"),
                Column("category", css_class="form-group col-md-4 mb-3"),
                css_class="row",
            ),
            Row(
                Column("date", css_class="form-group col-md-6 mb-3"),
                Column("time", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Field("location", css_class="form-control mb-3"),
            Field("description", css_class="form-control mb-3"),
            Field("image", css_class="form-control mb-3"),
            HTML(
                '<div id="form-feedback" class="alert alert-info d-none">Changes saved automatically...</div>'
            ),
            FormActions(
                Submit("submit", "Save Event", css_class="btn btn-primary btn-lg"),
                HTML(
                    '<button type="button" class="btn btn-secondary ms-2" onclick="history.back()">Cancel</button>'
                ),
            ),
        )

    def save(self, commit=True):
        event = super().save(commit=False)
        if self.user:
            event.organizer = self.user
        if commit:
            event.save()
        return event


class CategoryForm(forms.ModelForm):
    """Enhanced Category form with crispy styling"""

    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "needs-validation"
        self.helper.attrs = {"novalidate": True}

        self.helper.layout = Layout(
            Field("name", css_class="form-control mb-3"),
            Field("description", css_class="form-control mb-3"),
            FormActions(
                Submit("submit", "Save Category", css_class="btn btn-success"),
                HTML(
                    '<a href="{% url \'category_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'
                ),
            ),
        )


class ProfileForm(forms.ModelForm):
    """Enhanced Profile form with crispy styling"""

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        required=False, widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )

    class Meta:
        model = Profile
        fields = ["profile_picture", "phone_number", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "phone_number": forms.TextInput(attrs={"autocomplete": "tel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.form_class = "needs-validation"
        self.helper.attrs = {"novalidate": True}

        self.helper.layout = Layout(
            HTML('<h4 class="mb-3">Personal Information</h4>'),
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-3"),
                Column("last_name", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Field("email", css_class="form-control mb-3"),
            HTML('<hr><h4 class="mb-3">Profile Details</h4>'),
            Field("profile_picture", css_class="form-control mb-3"),
            Field("phone_number", css_class="form-control mb-3"),
            Field("bio", css_class="form-control mb-3"),
            FormActions(
                Submit("submit", "Update Profile", css_class="btn btn-primary"),
                HTML(
                    '<a href="{% url \'profile\' %}" class="btn btn-secondary ms-2">Cancel</a>'
                ),
            ),
        )

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Update user fields
        if profile.user:
            profile.user.first_name = self.cleaned_data["first_name"]
            profile.user.last_name = self.cleaned_data["last_name"]
            profile.user.email = self.cleaned_data["email"]
            if commit:
                profile.user.save()

        if commit:
            profile.save()
        return profile


class EventSearchForm(forms.Form):
    """Enhanced search form with crispy styling"""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search events by name, location, or description...",
                "class": "form-control",
                "hx-get": "{{ request.path }}",
                "hx-trigger": "input changed delay:300ms",
                "hx-target": "#events-container",
                "hx-swap": "innerHTML",
            }
        ),
        label="Search",
    )

    status = forms.ChoiceField(
        choices=Event.STATUS,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "hx-get": "{{ request.path }}",
                "hx-trigger": "change",
                "hx-target": "#events-container",
                "hx-swap": "innerHTML",
            }
        ),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "hx-get": "{{ request.path }}",
                "hx-trigger": "change",
                "hx-target": "#events-container",
                "hx-swap": "innerHTML",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_class = "mb-4"
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML('<div class="card"><div class="card-body">'),
            HTML('<h5 class="card-title mb-3">🔍 Find Events</h5>'),
            Row(
                Column(
                    Field(
                        "q",
                        hx_get="{{ request.path }}",
                        hx_trigger="input changed delay:300ms",
                        hx_target="#events-container",
                        hx_swap="innerHTML",
                    ),
                    css_class="col-md-6 mb-3",
                ),
                Column(
                    Field(
                        "status",
                        hx_get="{{ request.path }}",
                        hx_trigger="change",
                        hx_target="#events-container",
                        hx_swap="innerHTML",
                    ),
                    css_class="col-md-3 mb-3",
                ),
                Column(
                    Field(
                        "category",
                        hx_get="{{ request.path }}",
                        hx_trigger="change",
                        hx_target="#events-container",
                        hx_swap="innerHTML",
                    ),
                    css_class="col-md-3 mb-3",
                ),
                css_class="row",
            ),
            HTML(
                '<div class="text-muted small">Results update automatically as you type or change filters</div>'
            ),
            HTML("</div></div>"),
        )
