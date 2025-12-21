from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from django.core.mail import send_mail
from django.conf import settings
from ..decorators import admin_required
from ..utils.error_handler import ErrorHandlerService
from ..utils.messages import MessageService


class BaseViewMixin:
    """Base mixin for all views to handle common error handling and operations."""

    def handle_exception(
        self,
        request,
        exception,
        success_message="",
        error_message="An error occurred",
        redirect_url=None,
    ):
        """Common exception handling for all operations with user-friendly messages."""
        # Delegate to the centralized error handling service
        return ErrorHandlerService.handle_view_exception(
            request,
            exception,
            context=f"{self.__class__.__module__}.{self.__class__.__name__}",
            fallback_url=redirect_url or "event_list",
        )


def home(request):
    return render(request, "home.html")


def get_dashboard_stats():
    """
    Get dashboard statistics from DashboardStats model which is maintained by signals.
    Provides O(1) access to expensive aggregate queries.
    """
    from django.utils import timezone

    from ..models import DashboardStats

    today = timezone.now().date()

    # Get stats from the signal-maintained DashboardStats model
    # Use get_or_create to ensure a record always exists and avoid exception handling
    # The defaults will be used if the record doesn't exist, but signals should maintain it
    dashboard_stats, created = DashboardStats.objects.get_or_create(
        stat_date=today,
        defaults={
            "total_events": 0,
            "upcoming_events": 0,
            "past_events": 0,
            "total_participants": 0,
        },
    )
    return {
        "total_events": dashboard_stats.total_events,
        "upcoming_events": dashboard_stats.upcoming_events,
        "past_events": dashboard_stats.past_events,
        "total_participants": dashboard_stats.total_participants,
    }


@login_required
def dashboard_redirect(request):
    """Redirects users to their specific dashboard based on their role."""
    user = request.user
    if user.is_superuser:
        return redirect("admin_dashboard")

    # Use Django ORM to check if user is an organizer
    # This leverages existing indexes on auth_user.id, auth_user_groups.user_id,
    # auth_user_groups.group_id, and auth_group.name for better performance

    is_organizer = user.groups.filter(name="Organizer").exists()

    # Use dictionary lookup for role-based redirection
    role_map = {True: "organizer_dashboard", False: "participant_dashboard"}
    target_dashboard = role_map[is_organizer]
    return redirect(target_dashboard)


@admin_required
def admin_dashboard(request):
    """Admin Dashboard view."""
    return render(request, "dashboards/admin_dashboard.html")


@admin_required
def send_test_email(request):
    """Admin-only endpoint to send a test email via configured SMTP after deployment."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("admin_dashboard")

    to_email = request.POST.get("to") or request.user.email
    try:
        sent = send_mail(
            subject="EventMan SMTP Test",
            message=(
                "This is a test email from EventMan to verify SMTP delivery.\n\n"
                f"From: {settings.DEFAULT_FROM_EMAIL}\n"
                f"To: {to_email}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
        )
        if sent:
            messages.success(request, f"Test email sent to {to_email}.")
        else:
            messages.error(request, "Test email could not be sent (no error given).")
    except Exception as e:
        messages.error(request, f"SMTP error: {str(e)}")

    return redirect("admin_dashboard")


def _update_user_role(request):
    """Handle POST request to update user role."""
    from django.contrib.auth.models import Group, User

    user_id = request.POST.get("user_id")
    new_group_name = request.POST.get("group")

    try:
        user = User.objects.get(id=user_id)

        # Clear existing groups
        user.groups.clear()

        # Add user to new group if selected
        if new_group_name:
            group = Group.objects.get(name=new_group_name)
            user.groups.add(group)

        messages.success(request, f"Role updated for {user.username}")
    except (User.DoesNotExist, Group.DoesNotExist) as e:
        messages.error(request, f"Error updating role: {str(e)}")

    return redirect("manage_user_roles")


def _get_paginated_users(request):
    """Get paginated users with their groups."""
    from django.conf import settings
    from django.contrib.auth.models import Group as AuthGroup
    from django.contrib.auth.models import User
    from django.core.paginator import Paginator
    from django.db.models import Prefetch

    # Get paginated users with their groups more efficiently
    # The prefetch_related ensures we get the groups in a separate query rather than N+1
    all_users_qs = User.objects.prefetch_related(
        Prefetch("groups", queryset=AuthGroup.objects.only("name"))
    ).only("id", "username", "email", "first_name", "last_name")

    paginator = Paginator(
        all_users_qs, settings.USER_ADMIN_PAGINATION
    )  # Configurable users per page
    page_number = request.GET.get("page")
    users_page = paginator.get_page(page_number)

    return users_page


def _add_group_names_to_users(users_page):
    """Add group names to each user for efficient template access."""
    for user in users_page:
        user.group_names = [group.name for group in user.groups.all()]


@admin_required
def manage_user_roles(request):
    """Admin view to manage user roles/groups."""
    from django.contrib.auth.models import Group

    if request.method == "POST":
        return _update_user_role(request)

    # GET request - show users and their current roles with proper pagination
    users_page = _get_paginated_users(request)
    _add_group_names_to_users(users_page)

    groups = Group.objects.all()

    context = {
        "users": users_page,
        "groups": groups,
    }
    return render(request, "dashboards/manage_user_roles.html", context)


@login_required
def request_verification_email(request):
    """Allows users to manually request a verification email."""
    try:
        # Find the user's email address and send a confirmation
        email_address = (
            EmailAddress.objects.filter(user=request.user, email=request.user.email)
            .only("email", "verified")
            .first()
        )  # Only fetch necessary fields

        if email_address:
            # Use the send_confirmation method on the email address
            email_address.send_confirmation(request)
            messages.success(request, MessageService.VERIFICATION_EMAIL_SENT)
        else:
            messages.error(request, MessageService.VERIFICATION_ERROR)
    except Exception as e:
        messages.error(request, MessageService.format_email_error(str(e)))

    # Redirect back to referring page or to dashboard
    next_url = request.GET.get("next", "dashboard_redirect")
    return redirect(next_url)


@login_required
def verification_status(request):
    """Returns verification status for the current user with optimized DB access."""
    try:
        # Use only() to fetch only the verified field from the email record
        email_address = (
            EmailAddress.objects.filter(user=request.user, email=request.user.email)
            .only("verified")  # Only fetch the verified field
            .first()
        )
        is_verified = (
            email_address.verified if email_address else False
        )  # Return False if no record instead of assuming verified

        # Return JSON response for AJAX or redirect based on request type
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            from django.http import JsonResponse

            return JsonResponse({"verified": is_verified})
        else:
            # For direct access, redirect to dashboard
            return redirect("dashboard_redirect")
    except Exception as e:
        # Log the error for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.error(
            f"Error getting verification status for user {request.user.id}: {str(e)}"
        )

        # Return a proper error response instead of assuming verified
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            from django.http import JsonResponse

            return JsonResponse(
                {"verified": False, "error": "Verification check failed"}, status=500
            )
        else:
            messages.error(
                request, "There was an issue checking your verification status."
            )
            return redirect("dashboard_redirect")
