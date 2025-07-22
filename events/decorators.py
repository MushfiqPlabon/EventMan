from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse_lazy # Use reverse_lazy for decorators

def is_admin(user):
    """Checks if the user is a superuser (Admin)."""
    return user.is_authenticated and user.is_superuser

def is_organizer(user):
    """Checks if the user belongs to the 'Organizer' group."""
    return user.is_authenticated and user.groups.filter(name='Organizer').exists()

def is_participant(user):
    """Checks if the user belongs to the 'Participant' group."""
    return user.is_authenticated and user.groups.filter(name='Participant').exists()

# Decorators to restrict access
def admin_required(function=None, redirect_field_name=None, login_url=reverse_lazy('account_login')):
    """Decorator for views that require admin (superuser) access."""
    actual_decorator = user_passes_test(
        is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def organizer_required(function=None, redirect_field_name=None, login_url=reverse_lazy('account_login')):
    """Decorator for views that require 'Organizer' group membership."""
    actual_decorator = user_passes_test(
        is_organizer,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def participant_required(function=None, redirect_field_name=None, login_url=reverse_lazy('account_login')):
    """Decorator for views that require 'Participant' group membership."""
    actual_decorator = user_passes_test(
        is_participant,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# Combined decorator for Organizer or Admin access (e.g., for managing events)
def organizer_or_admin_required(function=None, redirect_field_name=None, login_url=reverse_lazy('account_login')):
    """Decorator for views that require 'Organizer' or Admin (superuser) access."""
    def check_user(user):
        return is_organizer(user) or is_admin(user)
    actual_decorator = user_passes_test(
        check_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator