from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.urls import reverse_lazy


def is_admin(user):
    """Checks if the user is a superuser (Admin)."""
    return user.is_authenticated and user.is_superuser


def _get_user_groups_cached(user):
    """Cache user group membership to avoid repeated database queries."""
    if not user.is_authenticated:
        return set()

    cache_key = f"user_groups_{user.id}"
    user_groups = cache.get(cache_key)
    if user_groups is None:
        user_groups = set(user.groups.values_list("name", flat=True))
        cache.set(
            cache_key, user_groups, settings.USER_GROUPS_CACHE_TIMEOUT
        )  # Configurable cache timeout
    return user_groups


def is_organizer(user):
    """Checks if the user belongs to the 'Organizer' group."""
    if not user.is_authenticated:
        return False
    user_groups = _get_user_groups_cached(user)
    return "Organizer" in user_groups


def is_participant(user):
    """Checks if the user belongs to the 'Participant' group."""
    if not user.is_authenticated:
        return False
    user_groups = _get_user_groups_cached(user)
    return "Participant" in user_groups


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
