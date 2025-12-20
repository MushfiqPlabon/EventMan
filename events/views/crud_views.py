"""
Core event functions that don't fit in the CRUD classification.
"""

import logging

import django_filters
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

from ..decorators import participant_required
from ..models import Category, Event, EventParticipant
from ..utils.messages import MessageService


class EventFilter(django_filters.FilterSet):
    """FilterSet for events using django-filter."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    date = django_filters.DateFilter()
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Event
        fields = ["name", "location", "date", "category"]


def event_list(request):
    """
    Lists all events, with search and filtering capabilities using django-filter.
    """
    from django.conf import settings
    from django.core.paginator import Paginator
    from django.db.models import Q

    # Map 'q' from template to 'name' or 'location' for GIN index utilization
    search_query = request.GET.get("q", "")
    query_params = request.GET.copy()

    # Use the custom manager's method for optimized queries
    events = Event.objects.with_related_data().order_by("date", "time")

    if search_query:
        # First apply exact or prefix matching to reduce dataset before trigram search
        # These operations use b-tree indexes which are O(log n) rather than O(n) trigram operations
        exact_match_filter = (
            Q(name__iexact=search_query)
            | Q(location__iexact=search_query)
            | Q(name__istartswith=search_query)
            | Q(location__istartswith=search_query)
        )

        # Apply exact/prefix matches first using efficient b-tree indexes
        preliminary_results = events.filter(exact_match_filter)

        # To avoid double query issue (once for exists() check, once for actual results),
        # we'll use a single evaluation approach
        # Evaluate the queryset once and use it for both existence check and final result
        preliminary_list = list(preliminary_results)

        if preliminary_list:
            # Convert back to a queryset to maintain compatibility with django-filter
            # Use the more efficient exact/prefix matches
            event_ids = [event.id for event in preliminary_list]
            events = Event.objects.filter(id__in=event_ids).order_by("date", "time")
        else:
            # Only use expensive trigram search if exact/prefix matches yield no results
            # This reduces the dataset size before applying expensive trigram operations
            events = events.filter(
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )

    # Apply filters using django-filter
    event_filter = EventFilter(query_params, queryset=events)

    # Implement pagination O(K)
    per_page = getattr(settings, "PARTICIPANT_DASHBOARD_PAGINATION", 9)
    paginator = Paginator(event_filter.qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get categories directly without caching
    categories = Category.objects.all().order_by("name")

    context = {
        "events": page_obj,
        "categories": categories,
        "filter": event_filter,
        "current_query": search_query,
        "current_status": request.GET.get("status", ""),
        "current_category": request.GET.get("category", ""),
    }

    return render(request, "events/event_list.html", context)


# Note: Not caching event_detail with cache_page because it may have user-specific content
# The main optimization is done by using the denormalized participant_count field
def event_detail(request, pk):
    """Displays detailed information for a single event."""
    # Use only required fields and the denormalized participant_count for O(1) access

    try:
        event = get_object_or_404(
            Event.objects.select_related("category", "organizer").only(
                "id",
                "name",
                "description",
                "date",
                "time",
                "location",
                "image",
                "participant_count",  # O(1) access to participant count
                "category__name",
                "organizer__first_name",
                "organizer__last_name",
            ),
            pk=pk,
        )
        context = {"event": event}
        return render(request, "events/event_detail.html", context)
    except Http404:
        messages.error(
            request,
            "The event you're looking for does not exist or may have been removed.",
        )
        return redirect("event_list")
    except Exception:
        messages.error(
            request,
            "An error occurred while retrieving the event details. Please try again later.",
        )
        return redirect("event_list")


def _validate_event_for_rsvp(request, event):
    """Validate that the event is valid for RSVP."""
    from ..models import validate_future_datetime

    try:
        validate_future_datetime(event.date, event.time)
    except ValidationError:
        messages.error(
            request,
            f"Cannot RSVP to event '{event.name}' as it has already occurred.",
        )
        return False
    return True


def _process_rsvp_action(event, user):
    """Process the RSVP action (create or delete)."""
    # Use get_or_create to handle both RSVP and cancellation in one operation
    # This reduces from 2 operations (exists + create/delete) to 1-2 operations
    event_participant, created = EventParticipant.objects.get_or_create(
        event=event, user=user
    )

    if not created:  # Was already RSVP'd, so we're cancelling
        # Delete the RSVP record
        event_participant.delete()
        msg_type = "info"
        msg_text = MessageService.format_rsvp_cancel_details(event.name)
        # Calculate new count for response
        new_count = max(0, event.participant_count - 1)
    else:  # New RSVP
        msg_type = "success"
        msg_text = MessageService.format_rsvp_success(event.name)
        # The participant_count was already incremented by the signal
        new_count = event.participant_count + 1

    return msg_type, msg_text, new_count, created


def _prepare_rsvp_response(request, msg_type, msg_text, created, new_count, event):
    """Prepare the response for RSVP action."""
    # Add user-friendly message
    getattr(messages, msg_type)(request, msg_text)

    # For AJAX requests, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse

        return JsonResponse(
            {
                "success": True,
                "message": msg_text,
                "is_participant": created,  # New state after toggle (True if newly RSVP'd)
                "participant_count": new_count,
            }
        )

    return redirect("event_detail", pk=event.pk)


def _handle_rsvp_error(request, user, pk, e):
    """Handle errors during RSVP processing."""
    # Log the error for debugging with proper Django logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error processing RSVP for user {user.id} and event {pk}: {str(e)}")

    # For AJAX requests, return JSON error response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse

        return JsonResponse(
            {
                "success": False,
                "message": "Sorry, there was an issue processing your RSVP. Please try again.",
            },
            status=500,
        )

    messages.error(
        request, "Sorry, there was an issue processing your RSVP. Please try again."
    )
    return redirect("event_list")


@participant_required  # User must be logged in as participant to RSVP
@csrf_protect
def rsvp_toggle(request, pk):
    """Toggles a user's RSVP status for an event with optimized performance and bloom filter integration."""
    # Check if it's a POST request first
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("event_list")

    # Define user before try block to ensure it's available in exception handler
    user = request.user

    try:
        with transaction.atomic():
            # Use select_for_update to prevent race conditions
            # Also get the participant count for updating the denormalized field
            event = get_object_or_404(
                Event.objects.select_for_update()
                .select_related("organizer")
                .only(
                    "id",
                    "name",
                    "date",
                    "time",
                    "participant_count",
                    "organizer__email",
                    "organizer__first_name",
                ),
                pk=pk,
            )

            # Validate that the event is valid for RSVP
            if not _validate_event_for_rsvp(request, event):
                return redirect("event_detail", pk=event.pk)

            # Process the RSVP action
            msg_type, msg_text, new_count, created = _process_rsvp_action(event, user)

            # Prepare the response
            return _prepare_rsvp_response(
                request, msg_type, msg_text, created, new_count, event
            )

    except Exception as e:
        return _handle_rsvp_error(request, user, pk, e)
