# events/forms.py
from django import forms
from .models import Category, Event

# Define common CSS classes as constants
# This makes it easy to change them in one place if your design evolves
COMMON_INPUT_CLASSES = 'form-input block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500'
COMMON_TEXTAREA_CLASSES = 'form-textarea block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500'
COMMON_SELECT_CLASSES = 'form-select block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm dark:bg-gray-700 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500'


class BaseForm(forms.ModelForm):
    """
    A base form that automatically applies common CSS classes and
    sets placeholders for all fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            
            if isinstance(field.widget, (forms.TextInput, forms.DateInput, forms.TimeInput, forms.EmailInput, forms.NumberInput)):
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{COMMON_INPUT_CLASSES} {current_classes}'.strip()
            elif isinstance(field.widget, forms.Textarea):
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{COMMON_TEXTAREA_CLASSES} {current_classes}'.strip()
            elif isinstance(field.widget, forms.Select):
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{COMMON_SELECT_CLASSES} {current_classes}'.strip()

            # Set placeholder if not explicitly defined and a label exists
            if 'placeholder' not in field.widget.attrs and field.label:
                field.widget.attrs['placeholder'] = field.label


class CategoryForm(BaseForm): # Inherit from BaseForm
    """
    Form for creating and updating Category objects.
    """
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }
        labels = {
            'name': 'Category Name',
            'description': 'Category Description',
        }

class EventForm(BaseForm): # Inherit from BaseForm
    """
    Form for creating and updating Event objects.
    """
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}), 
            'time': forms.TimeInput(attrs={'type': 'time'}), 
            'description': forms.Textarea(attrs={'rows': 3})
        }
        labels = {
            'name': 'Event Name',
            'description': 'Event Description',
            'date': 'Date',
            'time': 'Time',
            'location': 'Location',
            'category': 'Category'
        }