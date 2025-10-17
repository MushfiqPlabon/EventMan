from django.urls import path

from .views import (AdminDashboardView, CachedDashboardStatsView,
                    CachedEventDetailView, CategoryCreateView,
                    CategoryDeleteView, CategoryListView, CategoryUpdateView,
                    CustomPasswordChangeDoneView, CustomPasswordChangeView,
                    DashboardRedirectView, EventCreateView, EventDeleteView,
                    EventListView, EventUpdateView, HealthCheckView, HomeView,
                    OrganizerDashboardView, ParticipantDashboardView,
                    ParticipantListView, ProfileDetailView, ProfileUpdateView,
                    RSVPToggleView)

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
]
