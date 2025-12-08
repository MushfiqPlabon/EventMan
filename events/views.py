from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView
from django.conf import settings


class BaseEventViewMixin:
    """Base mixin for event views to handle common error handling and operations."""

    def handle_exception(
        self, request, exception, success_message="", error_message="An error occurred", redirect_url=None
    ):
        """Common exception handling for event operations with user-friendly messages."""
        # Don't expose technical details to users
        messages.error(
            request,
            f"Sorry, {error_message.lower()}. Please try again or contact support if the issue persists.",
        )

        # Use provided redirect URL if available, otherwise default to event_list
        if redirect_url:
            return redirect(redirect_url)
        else:
            # Try to get the referer or default to event_list
            referer = request.META.get('HTTP_REFERER')
            if referer and request.build_absolute_uri('/') in referer:
                return redirect(referer)
            else:
                return redirect("event_list")

    def invalidate_dashboard_cache(self, event_date=None):
        """Invalidate dashboard cache when needed."""
        from django.utils import timezone

        today = timezone.now().date()
        cache.delete(f"organizer_dashboard_stats_{today}")
        cache.delete(f"today_events_{today}")
        if event_date and event_date != today:
            cache.delete(f"organizer_dashboard_stats_{event_date}")
            cache.delete(f"today_events_{event_date}")


from .decorators import (admin_required, organizer_or_admin_required,
                         organizer_required, participant_required)
from .forms import CategoryForm, EventForm
from .models import Category, Event


def home(request):
    return render(request, "home.html")


@login_required
def dashboard_redirect(request):
    """Redirects users to their specific dashboard based on their role."""
    # O(1) lookup for dashboard redirection
    user = request.user
    if user.is_superuser:
        return redirect("admin_dashboard")

    # Use dictionary lookup for role-based redirection
    role_map = {
        True: "organizer_dashboard",
        False: "participant_dashboard"
    }

    # Determine if user is organizer - O(1) lookup
    is_organizer = user.groups.filter(name="Organizer").exists()
    target_dashboard = role_map[is_organizer]
    return redirect(target_dashboard)


@admin_required
def admin_dashboard(request):
    """Admin Dashboard view."""
    return render(request, "dashboards/admin_dashboard.html")


@admin_required
def manage_user_roles(request):
    """Admin view to manage user roles/groups."""
    from django.contrib.auth.models import Group, User

    if request.method == "POST":
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

    # GET request - show users and their current roles
    users = User.objects.prefetch_related("groups").all()
    groups = Group.objects.all()

    context = {
        "users": users,
        "groups": groups,
    }
    return render(request, "dashboards/manage_user_roles.html", context)


@organizer_required
def organizer_dashboard(request):
    """Organizer Dashboard view with stats and today's events."""
    today = timezone.now().date()

    # Cache dashboard statistics to reduce expensive aggregation queries - O(1) cache lookup
    cache_key = f"organizer_dashboard_stats_{today}"
    stats = cache.get(cache_key)
    if stats is None:
        # Optimized: Single query with conditional aggregation instead of multiple queries
        from django.db.models import Case, Count, IntegerField, When

        stats = Event.objects.aggregate(
            total_events=Count("id"),
            upcoming_events=Count(
                Case(When(date__gte=today, then=1), output_field=IntegerField())
            ),
            past_events=Count(
                Case(When(date__lt=today, then=1), output_field=IntegerField())
            ),
            total_participants=Count("participants", distinct=True),
        )
        cache.set(
            cache_key, stats, settings.DASHBOARD_CACHE_TIMEOUT
        )  # Configurable cache timeout

    # Today's Events Listing (optimized query) - cache this too
    today_events_cache_key = f"today_events_{today}"
    today_events = cache.get(today_events_cache_key)
    if today_events is None:
        today_events = Event.objects.select_related("category", "organizer").prefetch_related("participants").filter(date=today).order_by("time")
        cache.set(
            today_events_cache_key, today_events, settings.DASHBOARD_CACHE_TIMEOUT
        )  # Configurable cache timeout

    context = {
        "total_events": stats["total_events"],
        "upcoming_events": stats["upcoming_events"],
        "past_events": stats["past_events"],
        "total_participants": stats["total_participants"] or 0,
        "today_events": today_events,
    }
    return render(request, "dashboards/organizer_dashboard.html", context)


@participant_required  # Only participants can RSVP
def participant_dashboard(request):
    """Participant Dashboard view, showing RSVP'd events."""
    # Fetch events the current user has RSVP'd to with proper pagination
    # Use select_related to optimize category and organizer queries
    rsvp_events = request.user.events_joined.select_related("category", "organizer").order_by("date", "time")

    # Use Django's built-in Paginator
    paginator = Paginator(rsvp_events, 10)  # Show 10 events per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"rsvp_events": page_obj}
    return render(request, "dashboards/participant_dashboard.html", context)


def event_list(request):
    """
    Lists all events, with search and filtering capabilities.
    Search by event name or location.
    Filter by category, upcoming, or past.
    """
    # Optimize by removing unnecessary prefetch_related for participants to reduce memory usage
    events = Event.objects.select_related("category").order_by("date", "time")

    # Cache the categories since they don't change frequently - O(1) cache lookup
    from django.conf import settings

    cache_key = "all_categories"
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.all()
        cache.set(
            cache_key, categories, settings.CATEGORY_CACHE_TIMEOUT
        )  # Configurable cache timeout

    # Search functionality
    query = request.GET.get("q")
    if query:
        events = events.filter(Q(name__icontains=query) | Q(location__icontains=query))

    # Filtering by event status (upcoming, past) - O(1) dictionary lookup
    filter_status = request.GET.get("status")
    today = timezone.now().date()
    filter_map = {
        "upcoming": lambda e: e.filter(date__gte=today),
        "past": lambda e: e.filter(date__lt=today)
    }

    if filter_status in filter_map:
        events = filter_map[filter_status](events)

    # Filtering by category
    filter_category = request.GET.get("category")
    if filter_category:
        events = events.filter(
            category__name__iexact=filter_category
        )  # Case-insensitive category match

    context = {
        "events": events,
        "categories": categories,
        "current_query": query,
        "current_status": filter_status,
        "current_category": filter_category,
    }
    return render(request, "events/event_list.html", context)


def event_detail(request, pk):
    """Displays detailed information for a single event."""
    from django.db.models import Count

    # Use select_related and annotate for participant count to avoid N+1 queries
    event = get_object_or_404(
        Event.objects.select_related("category")
        .prefetch_related("participants")
        .annotate(participant_count=Count("participants")),
        pk=pk,
    )
    context = {"event": event}
    return render(request, "events/event_detail.html", context)


@method_decorator(organizer_or_admin_required, name="dispatch")
class EventCreateView(BaseEventViewMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def form_valid(self, form):
        try:
            event = form.save(commit=False)
            event.organizer = self.request.user
            event.save()
            # Invalidate dashboard cache when event is created
            self.invalidate_dashboard_cache(event.date)
            messages.success(self.request, "Event created successfully!")
            return redirect("event_detail", pk=event.pk)
        except Exception as e:
            return self.handle_exception(
                self.request, e, error_message="Error creating event", redirect_url="event_list"
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Event"
        return context


@method_decorator(organizer_or_admin_required, name="dispatch")
class EventUpdateView(BaseEventViewMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            event = self.get_object()
            if not request.user.is_superuser and event.organizer != request.user:
                messages.error(request, "You are not authorized to edit this event.")
                return redirect("event_detail", pk=event.pk)
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
            return redirect("event_list")
        except Exception as e:
            return self.handle_exception(request, e)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            # Invalidate dashboard cache when event is updated
            event = self.get_object()
            self.invalidate_dashboard_cache(event.date)
            messages.success(self.request, "Event updated successfully!")
            return response
        except Exception as e:
            return self.handle_exception(
                self.request, e, error_message="Error updating event", redirect_url="event_list"
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Event"
        try:
            context["event"] = self.get_object()
        except:
            context["event"] = None
        return context


@method_decorator(organizer_or_admin_required, name="dispatch")
class EventDeleteView(BaseEventViewMixin, DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("event_list")

    def dispatch(self, request, *args, **kwargs):
        try:
            event = self.get_object()
            if not request.user.is_superuser and event.organizer != request.user:
                messages.error(request, "You are not authorized to delete this event.")
                return redirect("event_detail", pk=event.pk)
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
            return redirect("event_list")
        except Exception as e:
            return self.handle_exception(request, e)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Get the event before deletion to access its date for cache invalidation
        event = self.get_object()
        event_date = event.date

        try:
            # Invalidate dashboard cache when event is deleted
            self.invalidate_dashboard_cache(event_date)
            messages.success(request, "Event deleted successfully!")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            return self.handle_exception(
                request, e, error_message="Error deleting event", redirect_url="event_list"
            )


@login_required  # User must be logged in to RSVP
def rsvp_toggle(request, pk):
    """Toggles a user's RSVP status for an event."""
    try:
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if request.method == "POST":
            is_participant = event.participants.filter(pk=user.pk).exists()
            # O(1) message selection based on action
            action_map = {
                True: ('info', f'You have un-RSVP\'d from "{event.name}".', lambda: event.participants.remove(user)),
                False: ('success', f'You have successfully RSVP\'d to "{event.name}"!', lambda: event.participants.add(user))
            }

            msg_type, msg_text, action = action_map[is_participant]
            action()  # Execute the appropriate action
            getattr(messages, msg_type)(request, msg_text)

            # Signal will handle sending the email if adding participant
            if not is_participant:
                pass  # Signal will handle sending the email
            # Invalidate dashboard cache when RSVP changes (participant count changes)
            BaseEventViewMixin().invalidate_dashboard_cache(event.date)
            return redirect("event_detail", pk=event.pk)
    except Exception:
        messages.error(
            request, "Sorry, there was an issue processing your RSVP. Please try again."
        )
        return redirect("event_list")

    return redirect("event_detail", pk=event.pk)  # Redirect if not a POST request


@method_decorator(organizer_or_admin_required, name="dispatch")
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            # Invalidate category cache when a new category is created
            cache.delete("all_categories")
            cache.delete("all_categories_sorted")
            messages.success(self.request, "Category created successfully!")
            return response
        except Exception:
            messages.error(
                self.request,
                "Sorry, there was an issue creating the category. Please try again.",
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Category"
        return context


def category_list(request):
    """Lists all categories."""
    # Use cached categories to improve performance - O(1) cache lookup
    cache_key = "all_categories_sorted"
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.all().order_by("name")
        cache.set(
            cache_key, categories, settings.CATEGORY_CACHE_TIMEOUT
        )  # Configurable cache timeout
    return render(request, "events/category_list.html", {"categories": categories})


@method_decorator(organizer_or_admin_required, name="dispatch")
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Category.DoesNotExist:
            messages.error(request, "Category not found.")
            return redirect("category_list")
        except Exception:
            messages.error(request, "Sorry, an error occurred. Please try again.")
            return redirect("category_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            # Invalidate category cache when a category is updated
            cache.delete("all_categories")
            cache.delete("all_categories_sorted")
            messages.success(self.request, "Category updated successfully!")
            return response
        except Exception:
            messages.error(
                self.request,
                "Sorry, there was an issue updating the category. Please try again.",
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Category"
        try:
            context["category"] = self.get_object()
        except:
            context["category"] = None
        return context


@method_decorator(organizer_or_admin_required, name="dispatch")
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "events/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Category.DoesNotExist:
            messages.error(request, "Category not found.")
            return redirect("category_list")
        except Exception:
            messages.error(request, "Sorry, an error occurred. Please try again.")
            return redirect("category_list")

    def delete(self, request, *args, **kwargs):
        try:
            # Invalidate category cache when a category is deleted
            cache.delete("all_categories")
            cache.delete("all_categories_sorted")
            messages.success(request, "Category deleted successfully!")
            return super().delete(request, *args, **kwargs)
        except Exception:
            messages.error(
                request,
                "Sorry, there was an issue deleting the category. Please try again.",
            )
            return redirect("category_list")
