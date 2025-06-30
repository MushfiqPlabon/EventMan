# events/forms.py
from django import forms
from .models import Category, Event, Participant

class CategoryForm(forms.ModelForm):
    """
    Form for creating and updating Category objects.
    """
    class Meta:
        model = Category
        fields = ['name', 'description'] # Fields from the Category model to include in the form
        # Optional: Add widgets for better control over form fields' HTML attributes
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'rows': 3, 'placeholder': 'Describe the category'}),
        }
        labels = {
            'name': 'Category Name',
            'description': 'Category Description',
        }

class EventForm(forms.ModelForm):
    """
    Form for creating and updating Event objects.
    """
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']
        # Widgets are crucial here for date/time pickers and styling
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Event Name'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'rows': 4, 'placeholder': 'Detailed description of the event'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500'}),
            'location': forms.TextInput(attrs={'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'e.g., Conference Hall A, Online'}),
            'category': forms.Select(attrs={'class': 'form-select block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500'}),
        }
        labels = {
            'name': 'Event Name',
            'description': 'Event Description',
            'date': 'Date',
            'time': 'Time',
            'location': 'Location',
            'category': 'Category'
        }

class ParticipantForm(forms.ModelForm):
    """
    Form for creating and updating Participant objects.
    Note: The 'events' ManyToManyField is typically managed separately
    or through the Event form itself, not usually when creating a participant directly.
    We'll keep this simple for now.
    """
    class Meta:
        model = Participant
        # We're excluding 'events' from this form for now, as it's better managed
        # when adding participants to an existing event.
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Participant Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'participant@example.com'}),
        }
        labels = {
            'name': 'Participant Name',
            'email': 'Email Address',
        }