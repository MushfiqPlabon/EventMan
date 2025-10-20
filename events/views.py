import json

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from decouple import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView)
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, View)
from django_filters.views import FilterView

from .constants import UserGroups
from .filters import CategoryFilter, EventFilter
from .forms.contact_form import ContactForm
from .forms.forms import CategoryForm, EventForm, EventSearchForm, ProfileForm
from .models import Category, Event, Payment, Profile
from .payment_utils import payment_handler
from .redis_utils import redis_client

User = get_user_model()


# Contact View
def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            full_message = f"Name: {name}\nEmail: {email}\n\n{message}"

            try:
                send_mail(
                    subject,  # Email subject
                    full_message,  # Email body
                    settings.DEFAULT_FROM_EMAIL,  # From email
                    [config("CONTACT_EMAIL", default="admin@eventman.com")],  # To email
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully!")
                return redirect("contact")  # Redirect to the contact page (GET request)
            except Exception as e:
                messages.error(request, f"There was an error sending your message: {e}")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})


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
        elif user.groups.filter(name=UserGroups.ORGANIZER).exists():
            return redirect("organizer_dashboard")
        else:
            return redirect("participant_dashboard")


class AdminDashboardView(SuperuserRequiredMixin, TemplateView):
    """Enhanced admin dashboard with live stats"""

    template_name = "dashboards/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_events = Event.objects.all()
        total_revenue = sum(
            event.ticket_price * event.tickets_sold for event in all_events
        )
        total_tickets_sold = sum(event.tickets_sold for event in all_events)

        context.update(
            {
                "total_events": all_events.count(),
                "total_users": User.objects.count(),
                "total_revenue": total_revenue,
                "total_tickets_sold": total_tickets_sold,
                "all_payments": Payment.objects.all()
                .select_related("user", "event")
                .order_by("-created"),
            }
        )
        return context


class OrganizerDashboardView(GroupRequiredMixin, TemplateView):
    """Enhanced organizer dashboard with live updates"""

    template_name = "dashboards/organizer_dashboard.html"
    group_required = [UserGroups.ORGANIZER]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_events = Event.objects.filter(organizer=user)

        total_revenue = sum(
            event.ticket_price * event.tickets_sold for event in user_events
        )
        total_tickets_sold = sum(event.tickets_sold for event in user_events)

        context.update(
            {
                "total_events": user_events.count(),
                "total_revenue": total_revenue,
                "total_tickets_sold": total_tickets_sold,
                "upcoming_events": user_events.filter(
                    date__gte=timezone.localdate(), status="published"
                ),
                "user_events_with_stats": user_events.annotate(
                    revenue=models.F("ticket_price") * models.F("tickets_sold")
                ).order_by("-created"),
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
            self.filterset = self.get_filterset(self.get_filterset_class())

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


class CheckoutView(LoginRequiredMixin, EventDetailView):
    """Displays the checkout page for an event, reusing EventDetailView's logic."""

    template_name = "events/checkout.html"


class EventCreateView(GroupRequiredMixin, CreateView):
    """Enhanced event creation with crispy forms"""

    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    group_required = [UserGroups.ORGANIZER]

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
    group_required = [UserGroups.ORGANIZER]

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
    group_required = [UserGroups.ORGANIZER]

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
    group_required = [UserGroups.ORGANIZER]

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)


class CategoryUpdateView(GroupRequiredMixin, UpdateView):
    """Enhanced category update"""

    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")
    group_required = [UserGroups.ORGANIZER]

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully!")
        return super().form_valid(form)


class CategoryDeleteView(GroupRequiredMixin, DeleteView):
    """Enhanced category deletion"""

    model = Category
    template_name = "events/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")
    group_required = [UserGroups.ORGANIZER]

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
    group_required = [UserGroups.ORGANIZER]

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
        elif request.user.groups.filter(name=UserGroups.ORGANIZER).exists():
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


# ===== PAYMENT VIEWS =====


@login_required
@require_http_methods(["POST"])
def initiate_payment(request, pk):
    """Secure payment initiation with CSRF protection."""
    event = get_object_or_404(Event, pk=pk, status="published")

    # Check if user already has a valid ticket
    if request.user in event.participants.all():
        messages.info(request, "You already have a ticket for this event!")
        return redirect("event_detail", pk=pk)

    # Create payment session
    result = payment_handler.create_payment_session(request, event, request.user)

    if result["success"]:
        return redirect(result["gateway_url"])
    else:
        messages.error(
            request,
            f"Payment initiation failed: {result.get('error', 'Unknown error')}",
        )
        return redirect("event_detail", pk=pk)


@require_http_methods(["GET", "POST"])
def payment_success(request):
    """Secure payment success handler."""
    if request.method == "GET":
        # Handle GET requests (user redirected from payment gateway)
        tran_id = request.GET.get("tran_id")
        if not tran_id:
            messages.error(request, "Invalid payment response.")
            return redirect("event_list")
    else:
        # Handle POST requests (callback from payment gateway)
        tran_id = request.POST.get("tran_id")

    if not tran_id:
        messages.error(request, "Missing transaction information.")
        return redirect("event_list")

    # Validate payment
    result = payment_handler.validate_payment(request.POST or request.GET)

    if result["success"]:
        event = result["event"]
        messages.success(request, f"Payment successful for {event.name}!")
        return render(request, "payment_success.html", {"event": event})
    else:
        messages.error(
            request,
            f"Payment validation failed: {result.get('error', 'Unknown error')}",
        )
        return redirect("event_list")


@require_http_methods(["GET", "POST"])
def payment_fail(request):
    """Secure payment failure handler."""
    # Handle both GET and POST requests
    payment_data = request.POST if request.method == "POST" else request.GET

    # Handle failed payment
    payment_handler.handle_failed_payment(payment_data)

    messages.error(request, "Payment failed or was cancelled.")
    return render(request, "payment_fail.html")


@require_http_methods(["POST"])
def payment_ipn(request):
    """Secure IPN handler for SSLCommerz notifications."""
    # For production, implement IP whitelisting and signature verification

    # Log IPN request for monitoring
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"IPN received from IP: {request.META.get('REMOTE_ADDR')}")

    # Validate payment
    result = payment_handler.validate_payment(request.POST)

    if result["success"]:
        logger.info(f"IPN processed successfully: {request.POST.get('tran_id')}")
        return HttpResponse("IPN Processed")
    else:
        logger.warning(f"IPN validation failed: {result.get('error')}")
        return HttpResponse("IPN Received")


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
        elif request.user.groups.filter(name=UserGroups.ORGANIZER).exists():
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


def get_live_stats_htmx(request):
    total_events = Event.objects.filter(status="published").count()
    total_categories = Category.objects.count()
    all_events = Event.objects.all()
    total_tickets_sold = sum(event.tickets_sold for event in all_events)

    context = {
        "total_events": total_events,
        "total_categories": total_categories,
        "total_tickets_sold": total_tickets_sold,
    }
    return render(request, "events/_live_stats.html", context)


@login_required
def get_participant_payments_htmx(request):
    user_payments = (
        Payment.objects.filter(user=request.user)
        .select_related("event")
        .order_by("-created")
    )
    context = {
        "user": request.user,
        "user_payments": user_payments,
    }
    return render(request, "events/_participant_payments.html", context)


@login_required
def get_organizer_stats_htmx(request):
    user = request.user
    user_events = Event.objects.filter(organizer=user)

    total_revenue = sum(
        event.ticket_price * event.tickets_sold for event in user_events
    )
    total_tickets_sold = sum(event.tickets_sold for event in user_events)
    upcoming_events_count = user_events.filter(
        date__gte=timezone.localdate(), status="published"
    ).count()

    context = {
        "total_revenue": total_revenue,
        "total_tickets_sold": total_tickets_sold,
        "upcoming_events_count": upcoming_events_count,
    }
    return render(request, "events/_organizer_stats.html", context)


@login_required
def get_organizer_events_htmx(request):
    user = request.user
    user_events_with_stats = (
        Event.objects.filter(organizer=user)
        .annotate(revenue=models.F("ticket_price") * models.F("tickets_sold"))
        .order_by("-created")
    )

    context = {
        "user_events_with_stats": user_events_with_stats,
    }
    return render(request, "events/_organizer_events.html", context)


@login_required
def get_admin_stats_htmx(request):
    all_events = Event.objects.all()
    total_revenue = sum(event.ticket_price * event.tickets_sold for event in all_events)
    total_tickets_sold = sum(event.tickets_sold for event in all_events)
    total_events = all_events.count()
    total_users = User.objects.count()

    context = {
        "total_revenue": total_revenue,
        "total_tickets_sold": total_tickets_sold,
        "total_events": total_events,
        "total_users": total_users,
    }
    return render(request, "events/_admin_stats.html", context)


@login_required
def get_admin_payments_htmx(request):
    all_payments = (
        Payment.objects.all().select_related("user", "event").order_by("-created")
    )
    context = {
        "all_payments": all_payments,
    }
    return render(request, "events/_admin_payments.html", context)
