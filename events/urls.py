# events/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Base URL for the dashboard/home
    path('', views.DashboardView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'), # Added for clarity

    # Event URLs
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/new/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)