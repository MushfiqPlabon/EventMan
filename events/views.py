import json

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView)
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, View)
from django_filters.views import FilterView

from .filters import CategoryFilter, EventFilter
from .forms import CategoryForm, EventForm, EventSearchForm, ProfileForm
from .models import Category, Event, Profile
from .redis_utils import redis_client

User = get_user_model()

# ===== HOME & DASHBOARD VIEWS =====


class HomeView(TemplateView):
    """Enhanced home page"""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_events"] = Event.objects.filter(
            status="published", date__gte=timezone.localdate()
        ).order_by("date")[:6]
        context["total_events"] = Event.objects.filter(status="published").count()
        context["total_categories"] = Category.objects.count()
        return context


class DashboardRedirectView(LoginRequiredMixin, View):
    """Smart dashboard redirect based on user role"""

    def get(self, request):
        user = request.user

        if user.is_superuser:
            return redirect("admin_dashboard")
        elif user.groups.filter(name="Organizer").exists():
            return redirect("organizer_dashboard")
        else:
            return redirect("participant_dashboard")


class AdminDashboardView(SuperuserRequiredMixin, TemplateView):
    """Enhanced admin dashboard with live stats"""

    template_name = "dashboards/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.localdate()

        context.update(
            {
                "total_events": Event.objects.count(),
                "total_users": User.objects.count(),
                "total_participants": User.objects.filter(events_joined__isnull=False)
                .distinct()
                .count(),
                "past_events": Event.objects.filter(date__lt=current_date).count(),
                "upcoming_events": Event.objects.filter(
                    date__gte=current_date, status="published"
                ).count(),
                "today_events": Event.objects.filter(
                    date=current_date, status="published"
                ),
                "recent_events": Event.objects.order_by("-created")[:5],
                "current_date": current_date,
            }
        )
        return context


class OrganizerDashboardView(GroupRequiredMixin, TemplateView):
    """Enhanced organizer dashboard with live updates"""

    template_name = "dashboards/organizer_dashboard.html"
    group_required = ["Organizer"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.localdate()
        user_events = Event.objects.filter(organizer=self.request.user)

        context.update(
            {
                "total_events": user_events.count(),
                "total_participants": User.objects.filter(
                    events_joined__organizer=self.request.user
                )
                .distinct()
                .count(),
                "past_events": user_events.filter(date__lt=current_date).count(),
                "upcoming_events": user_events.filter(
                    date__gte=current_date, status="published"
                ).count(),
                "today_events": user_events.filter(
                    date=current_date, status="published"
                ),
                "current_date": current_date,
            }
        )
        return context


class ParticipantDashboardView(LoginRequiredMixin, TemplateView):
    """Enhanced participant dashboard"""

    template_name = "dashboards/participant_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_date = timezone.localdate()

        context.update(
            {
                "my_events": user.events_joined.filter(status="published"),
                "upcoming_events": user.events_joined.filter(
                    date__gte=current_date, status="published"
                ).order_by("date"),
                "past_events": user.events_joined.filter(date__lt=current_date),
                "recommended_events": Event.objects.filter(
                    status="published", date__gte=current_date
                ).exclude(participants=user)[:6],
            }
        )
        return context


# ===== EVENT VIEWS WITH HTMX =====


class EventListView(FilterView):
    """Enhanced event list with django-filter and HTMX"""

    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    filterset_class = EventFilter
    paginate_by = 12

    def get_queryset(self):
        return (
            Event.objects.select_related("category", "organizer")
            .prefetch_related("participants")
            .order_by("date", "time")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["search_form"] = EventSearchForm(self.request.GET)
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            # Return filtered events for HTMX requests
            self.object_list = self.get_queryset()
            self.get_context_data()

            html = render_to_string(
                "events/_event_grid.html",
                {"events": self.filterset.qs, "user": request.user},
            )
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)


class EventDetailView(DetailView):
    """Enhanced event detail with HTMX RSVP"""

    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.select_related("category", "organizer").prefetch_related(
            "participants"
        )


class EventCreateView(GroupRequiredMixin, CreateView):
    """Enhanced event creation with crispy forms"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    group_required = ["Organizer"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Event created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("event_detail", kwargs={"pk": self.object.pk})


class EventUpdateView(GroupRequiredMixin, UserPassesTestMixin, UpdateView):
    """Enhanced event update with crispy forms"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    group_required = ["Organizer"]

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_superuser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Event updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("event_detail", kwargs={"pk": self.object.pk})


class EventDeleteView(GroupRequiredMixin, UserPassesTestMixin, DeleteView):
    """Enhanced event deletion"""

    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("event_list")
    group_required = ["Organizer"]

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Event deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ===== HTMX RSVP VIEW =====


class RSVPToggleView(LoginRequiredMixin, View):
    """HTMX-powered RSVP toggle"""

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, status="published")
        user = request.user

        user_is_participant = user in event.participants.all()

        if user_is_participant:
            event.participants.remove(user)
            message = "RSVP cancelled successfully!"
            btn_class = "btn-primary"
            btn_text = "📝 RSVP"
        else:
            event.participants.add(user)
            message = "RSVP confirmed! See you at the event!"
            btn_class = "btn-success"
            btn_text = "✅ RSVP'd"

        if request.htmx:
            # Return updated button HTML
            html = f"""
            <button hx-post="{reverse('rsvp_toggle', kwargs={'pk': event.pk})}"
                    hx-swap="outerHTML"
                    class="{btn_class} text-sm py-2 px-4">
                {btn_text}
            </button>
            """
            response = HttpResponse(html)
            response["HX-Trigger"] = json.dumps(
                {"showMessage": message, "updateCount": event.participants.count()}
            )
            return response

        # Fallback for non-HTMX requests
        messages.success(request, message)
        return redirect("event_detail", pk=event.pk)


# ===== CATEGORY VIEWS =====


class CategoryListView(FilterView):
    """Enhanced category list with filtering"""

    model = Category
    template_name = "events/category_list.html"
    context_object_name = "categories"
    filterset_class = CategoryFilter

    def get_queryset(self):
        return Category.objects.annotate(
            event_count=Count("event", filter=Q(event__status="published"))
        ).order_by("name")


class CategoryCreateView(GroupRequiredMixin, CreateView):
    """Enhanced category creation"""

    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")
    group_required = ["Organizer"]

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)


class CategoryUpdateView(GroupRequiredMixin, UpdateView):
    """Enhanced category update"""

    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")
    group_required = ["Organizer"]

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully!")
        return super().form_valid(form)


class CategoryDeleteView(GroupRequiredMixin, DeleteView):
    """Enhanced category deletion"""

    model = Category
    template_name = "events/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")
    group_required = ["Organizer"]

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Category deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ===== PROFILE VIEWS =====


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """Enhanced profile view"""

    model = Profile
    template_name = "account/profile.html"
    context_object_name = "profile"

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Enhanced profile update with crispy forms"""

    model = Profile
    form_class = ProfileForm
    template_name = "account/profile_update.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)


# ===== UTILITY VIEWS =====


class ParticipantListView(GroupRequiredMixin, ListView):
    """Enhanced participant list"""

    model = User
    template_name = "events/participant_list.html"
    context_object_name = "participants"
    group_required = ["Organizer"]

    def get_queryset(self):
        return (
            User.objects.filter(events_joined__isnull=False)
            .distinct()
            .annotate(event_count=Count("events_joined"))
            .order_by("-event_count")
        )


# ===== AJAX ENDPOINTS =====


class DashboardStatsView(LoginRequiredMixin, View):
    """AJAX endpoint for live dashboard stats"""

    def get(self, request):
        current_date = timezone.now().date()

        if request.user.is_superuser:
            stats = {
                "total_events": Event.objects.count(),
                "total_participants": User.objects.filter(events_joined__isnull=False)
                .distinct()
                .count(),
                "past_events": Event.objects.filter(date__lt=current_date).count(),
                "upcoming_events": Event.objects.filter(
                    date__gte=current_date, status="published"
                ).count(),
            }
        elif request.user.groups.filter(name="Organizer").exists():
            user_events = Event.objects.filter(organizer=request.user)
            stats = {
                "total_events": user_events.count(),
                "total_participants": User.objects.filter(
                    events_joined__organizer=request.user
                )
                .distinct()
                .count(),
                "past_events": user_events.filter(date__lt=current_date).count(),
                "upcoming_events": user_events.filter(
                    date__gte=current_date, status="published"
                ).count(),
            }
        else:
            user_events = request.user.events_joined.all()
            stats = {
                "total_events": user_events.count(),
                "upcoming_events": user_events.filter(
                    date__gte=current_date, status="published"
                ).count(),
                "past_events": user_events.filter(date__lt=current_date).count(),
            }

        return JsonResponse(stats)


# Import existing password change views


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Enhanced password change view"""

    template_name = "account/password_change.html"
    success_url = reverse_lazy("password_change_done")


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """Enhanced password change done view"""

    template_name = "account/password_change_done.html"


# Health check endpoint for Vercel monitoring
class HealthCheckView(View):
    """Simple health check for deployment monitoring"""

    def get(self, request):
        return JsonResponse(
            {
                "status": "healthy",
                "service": "EventMan",
                "version": "1.0.0",
                "features": [
                    "Django MVT",
                    "Tailwind CSS",
                    "HTMX Reactivity",
                    "Live Updates",
                    "Mobile Responsive",
                ],
                "environment": "production" if not settings.DEBUG else "development",
            }
        )


# Enhanced dashboard with Redis caching


class CachedDashboardStatsView(DashboardStatsView):
    """Enhanced dashboard stats with Redis caching"""

    def get(self, request):
        # Try to get cached stats first
        cached_stats = redis_client.get_event_stats()

        if cached_stats:
            return JsonResponse(cached_stats)

        # Generate fresh stats
        current_date = timezone.now().date()

        if request.user.is_superuser:
            stats = {
                "total_events": Event.objects.count(),
                "total_participants": User.objects.filter(events_joined__isnull=False)
                .distinct()
                .count(),
                "past_events": Event.objects.filter(date__lt=current_date).count(),
                "upcoming_events": Event.objects.filter(
                    date__gte=current_date, status="published"
                ).count(),
                "cache_status": "fresh",
            }
        elif request.user.groups.filter(name="Organizer").exists():
            user_events = Event.objects.filter(organizer=request.user)
            stats = {
                "total_events": user_events.count(),
                "total_participants": User.objects.filter(
                    events_joined__organizer=request.user
                )
                .distinct()
                .count(),
                "past_events": user_events.filter(date__lt=current_date).count(),
                "upcoming_events": user_events.filter(
                    date__gte=current_date, status="published"
                ).count(),
                "cache_status": "fresh",
            }
        else:
            user_events = request.user.events_joined.all()
            stats = {
                "total_events": user_events.count(),
                "upcoming_events": user_events.filter(
                    date__gte=current_date, status="published"
                ).count(),
                "past_events": user_events.filter(date__lt=current_date).count(),
                "cache_status": "fresh",
            }

        # Cache the stats for 5 minutes
        redis_client.set_event_stats(stats, timeout=300)

        return JsonResponse(stats)


# Enhanced event detail view with Redis view tracking
class CachedEventDetailView(EventDetailView):
    """Enhanced event detail with view tracking"""

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Increment view count
        event_id = kwargs.get("pk")
        if event_id:
            redis_client.increment_event_views(event_id)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add view count to context
        event_id = self.object.pk
        context["view_count"] = redis_client.get_event_views(event_id)

        return context
