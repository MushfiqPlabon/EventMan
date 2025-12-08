# event_management_system/events/urls.py

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path(
        "dashboard/admin/manage-roles/",
        views.manage_user_roles,
        name="manage_user_roles",
    ),
    path("dashboard/organizer/", views.organizer_dashboard, name="organizer_dashboard"),
    path(
        "dashboard/participant/",
        views.participant_dashboard,
        name="participant_dashboard",
    ),
    # Event URLs
    path("events/", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/new/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path(
        "events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"
    ),
    path(
        "events/<int:pk>/rsvp_toggle/", views.rsvp_toggle, name="rsvp_toggle"
    ),  # RSVP URL
    # Category URLs
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
]
