from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy


def is_admin(user):
    """Checks if the user is a superuser (Admin)."""
    return user.is_authenticated and user.is_superuser


def is_organizer(user):
    """Checks if the user belongs to the 'Organizer' group."""
    if not user.is_authenticated:
        return False
    # Use Django ORM for better maintainability and security

    return user.groups.filter(name="Organizer").exists()


def is_participant(user):
    """Checks if the user belongs to the 'Participant' group."""
    if not user.is_authenticated:
        return False
    # Use Django ORM for better maintainability and security

    return user.groups.filter(name="Participant").exists()


# Decorators to restrict access - using single helper for all
def _restricted_access(user_check_func):
    def decorator(func=None):
        actual_decorator = user_passes_test(
            user_check_func, login_url=reverse_lazy("account_login")
        )
        return actual_decorator(func) if func else actual_decorator

    return decorator


admin_required = _restricted_access(is_admin)
organizer_required = _restricted_access(is_organizer)
participant_required = _restricted_access(is_participant)


def _check_organizer_or_admin(user):
    return is_organizer(user) or is_admin(user)


organizer_or_admin_required = _restricted_access(_check_organizer_or_admin)
