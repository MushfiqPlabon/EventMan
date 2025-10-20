from django.urls import path

from . import views
from .views import (AdminDashboardView, CachedDashboardStatsView,
                    CachedEventDetailView, CategoryCreateView,
                    CategoryDeleteView, CategoryListView, CategoryUpdateView,
                    CheckoutView, CustomPasswordChangeDoneView,
                    CustomPasswordChangeView, DashboardRedirectView,
                    EventCreateView, EventDeleteView, EventListView,
                    EventUpdateView, HealthCheckView, HomeView,
                    OrganizerDashboardView, ParticipantDashboardView,
                    ParticipantListView, ProfileDetailView, ProfileUpdateView,
                    RSVPToggleView, get_admin_payments_htmx,
                    get_admin_stats_htmx, get_live_stats_htmx,
                    get_organizer_events_htmx, get_organizer_stats_htmx,
                    get_participant_payments_htmx)

urlpatterns = [
    # Home and dashboard URLs
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardRedirectView.as_view(), name="dashboard_redirect"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path(
        "dashboard/organizer/",
        OrganizerDashboardView.as_view(),
        name="organizer_dashboard",
    ),
    path(
        "dashboard/participant/",
        ParticipantDashboardView.as_view(),
        name="participant_dashboard",
    ),
    path(
        "dashboard/stats/", CachedDashboardStatsView.as_view(), name="dashboard_stats"
    ),
    # Participant URLs
    path("participants/", ParticipantListView.as_view(), name="participant_list"),
    # Event URLs with HTMX support
    path("events/", EventListView.as_view(), name="event_list"),
    path("events/<int:pk>/", CachedEventDetailView.as_view(), name="event_detail"),
    path("events/new/", EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", EventUpdateView.as_view(), name="event_update"),
    path("events/<int:pk>/delete/", EventDeleteView.as_view(), name="event_delete"),
    path("events/<int:pk>/checkout/", CheckoutView.as_view(), name="event_checkout"),
    path("events/<int:pk>/rsvp/", RSVPToggleView.as_view(), name="rsvp_toggle"),
    # Category URLs
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/new/", CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # Profile URLs
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_update"),
    path(
        "password/change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "password/change/done/",
        CustomPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # Health check for Vercel
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("live-stats/", get_live_stats_htmx, name="live_stats_htmx"),
    path(
        "participant-payments/",
        get_participant_payments_htmx,
        name="participant_payments_htmx",
    ),
    path("organizer-stats/", get_organizer_stats_htmx, name="organizer_stats_htmx"),
    path("organizer-events/", get_organizer_events_htmx, name="organizer_events_htmx"),
    path("admin-stats/", get_admin_stats_htmx, name="admin_stats_htmx"),
    path("admin-payments/", get_admin_payments_htmx, name="admin_payments_htmx"),
    # Payment URLs
    path(
        "event/<int:pk>/initiate_payment/",
        views.initiate_payment,
        name="initiate_payment",
    ),
    path("payment_success/", views.payment_success, name="payment_success"),
    path("payment_fail/", views.payment_fail, name="payment_fail"),
    path("payment_ipn/", views.payment_ipn, name="payment_ipn"),
    path("contact/", views.contact_view, name="contact"),  # New contact page URL
]
