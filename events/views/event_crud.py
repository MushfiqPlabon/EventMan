"""
Event-specific CRUD views using django-extra-views.
"""

from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from ..decorators import (organizer_or_admin_required, organizer_required,
                          participant_required)
from ..forms import EventForm
from ..models import Event
from ..utils.messages import MessageService
from .generic_django_extra_views import (GenericCreateView, GenericDeleteView,
                                         GenericUpdateView)
from .main_views import get_dashboard_stats


@method_decorator(organizer_or_admin_required, name="dispatch")
class EventCreateView(GenericCreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_message = MessageService.EVENT_CREATED_SUCCESS
    error_prefix = "creating event"

    def get_success_url(self):
        return reverse_lazy("event_detail", kwargs={"pk": self.object.pk})


@method_decorator(organizer_or_admin_required, name="dispatch")
class EventUpdateView(GenericUpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_message = MessageService.EVENT_UPDATED_SUCCESS
    error_prefix = "updating event"

    def get_success_url(self):
        return reverse_lazy("event_detail", kwargs={"pk": self.object.pk})


@method_decorator(organizer_or_admin_required, name="dispatch")
class EventDeleteView(GenericDeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("event_list")
    success_message = MessageService.EVENT_DELETED_SUCCESS


@organizer_required
def organizer_dashboard(request):
    """Organizer Dashboard view with stats and today's events isolated to the current user."""
    # Use DashboardStats model for O(1) access to dashboard statistics
    stats = get_dashboard_stats()

    from django.core.paginator import Paginator
    from django.utils import timezone

    today = timezone.now().date()

    # Today's Events Listing (optimized and ISOLATED query)
    today_events_qs = (
        Event.objects.select_related("category", "organizer")
        .filter(date=today, organizer=request.user)  # Isolation Fix
        .only(
            "id",
            "name",
            "date",
            "time",
            "location",
            "category__name",
            "organizer__first_name",
            "organizer__last_name",
            "participant_count",
        )
        .order_by("time")
    )

    # Implement pagination for organizer dashboard
    per_page = getattr(settings, "PARTICIPANT_DASHBOARD_PAGINATION", 10)
    paginator = Paginator(today_events_qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "total_events": stats.get("total_events", 0),
        "upcoming_events": stats.get("upcoming_events", 0),
        "past_events": stats.get("past_events", 0),
        "total_participants": stats.get("total_participants", 0),
        "today_events": page_obj,
    }
    return render(request, "dashboards/organizer_dashboard.html", context)


@participant_required  # Only participants can RSVP
def participant_dashboard(request):
    """Participant Dashboard view, showing RSVP'd events."""
    # Fetch events the current user has RSVP'd to with proper pagination
    # Use select_related to optimize category and organizer queries and only() to minimize memory usage
    rsvp_events = (
        request.user.events_joined.select_related("category", "organizer")
        .only(
            "id",
            "name",
            "date",
            "time",
            "location",
            "category__name",
            "organizer__first_name",
            "organizer__last_name",
        )
        .order_by("date", "time")
    )

    # Use Django's built-in Paginator
    paginator = Paginator(
        rsvp_events, settings.PARTICIPANT_DASHBOARD_PAGINATION
    )  # Configurable events per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"rsvp_events": page_obj}
    return render(request, "dashboards/participant_dashboard.html", context)
