# event_management_system/events/urls.py

from django.urls import path

from .views.category_crud import (CategoryCreateView, CategoryDeleteView,
                                  CategoryUpdateView, category_list)
from .views.crud_views import event_detail, event_list, rsvp_toggle
from .views.event_crud import (EventCreateView, EventDeleteView,
                               EventUpdateView, organizer_dashboard,
                               participant_dashboard)
from .views.main_views import (admin_dashboard, dashboard_redirect, home,
                               manage_user_roles, request_verification_email,
                               verification_status)

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path(
        "dashboard/admin/manage-roles/",
        manage_user_roles,
        name="manage_user_roles",
    ),
    path("dashboard/organizer/", organizer_dashboard, name="organizer_dashboard"),
    path(
        "dashboard/participant/",
        participant_dashboard,
        name="participant_dashboard",
    ),
    # Event URLs
    path("events/", event_list, name="event_list"),
    path("events/<int:pk>/", event_detail, name="event_detail"),
    path("events/new/", EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", EventUpdateView.as_view(), name="event_update"),
    path("events/<int:pk>/delete/", EventDeleteView.as_view(), name="event_delete"),
    path("events/<int:pk>/rsvp_toggle/", rsvp_toggle, name="rsvp_toggle"),  # RSVP URL
    path(
        "request_verification_email/",
        request_verification_email,
        name="request_verification_email",
    ),  # Allow users to request verification email manually
    path(
        "verification_status/", verification_status, name="verification_status"
    ),  # Check verification status
    # Category URLs
    path("categories/", category_list, name="category_list"),
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
]
