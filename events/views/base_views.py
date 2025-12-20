"""
Generic CRUD views using django-extra-views to reduce code duplication.
"""

from braces.views import StaffuserRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from ..utils.error_handler import FormErrorHandler


class BaseAuthRequiredView(LoginRequiredMixin):
    """Base view with authentication requirement."""

    login_url = "/accounts/login/"


class OrganizerRequiredMixin(UserPassesTestMixin):
    """Mixin to require organizer role."""

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True

        # Use a direct optimized query with JOINs for better performance
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM auth_user_groups u_g
                    INNER JOIN auth_group g ON u_g.group_id = g.id
                    WHERE u_g.user_id = %s AND g.name = 'Organizer'
                )
            """,
                [user.id],
            )
            return cursor.fetchone()[0]


class AdminRequiredMixin(StaffuserRequiredMixin):
    """Mixin to require admin role."""


class BaseEventCategoryView(BaseAuthRequiredView):
    """Base view for event and category operations."""

    def handle_error(self, form, error_prefix):
        """Common error handling for forms."""
        FormErrorHandler.handle_form_errors(self.request, form, error_prefix)

        error_msg = str(form.errors)
        messages.error(self.request, f"Error: {error_msg}")

    def get_success_message(self):
        """Get success message based on operation - to be overridden."""
        return "Operation completed successfully"
