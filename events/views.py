# events/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse_lazy # For redirecting after successful form submission
from .models import Event, Category # Removed Participant import
from .forms import EventForm, CategoryForm # Removed ParticipantForm import
from django.db.models import Q, Sum, Count # For filtering and aggregating
from django.utils import timezone # Django's timezone utilities
from datetime import date # For date-only comparisons
from django.contrib.auth.mixins import LoginRequiredMixin # Will be used for authentication later


# --- Home View ---
def home(request):
    # Get upcoming 5 events in the project's local timezone
    upcoming_events = Event.objects.filter(
        Q(date__gt=timezone.localdate()) |
        Q(date=timezone.localdate(), time__gte=timezone.localtime(timezone.now()).time())
    ).order_by('date', 'time')[:5].select_related('category') # Optimize by selecting category

    return render(request, 'events/home.html', {
        'message': 'Welcome to the Event Management System!',
        'upcoming_events': upcoming_events,
    })

# --- Event CRUD Views ---

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10 # Display 10 events per page

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        category_filter = self.request.GET.get('category')
        date_filter = self.request.GET.get('date')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
        if category_filter:
            queryset = queryset.filter(category__id=category_filter)
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset.select_related('category') # Optimize query for related category data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all() # Pass all categories for filtering
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list') # Redirect to event list after creation

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    context_object_name = 'event' # Ensure the object is passed as 'event'
    success_url = reverse_lazy('event_list')

class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    context_object_name = 'event'
    success_url = reverse_lazy('event_list')

# --- Category CRUD Views ---

class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'events/category_detail.html'
    context_object_name = 'category'

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'events/category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category_list')


# --- Dashboard View ---
class DashboardView(ListView):
    model = Event
    template_name = 'events/dashboard.html'
    context_object_name = 'events_today' # Changed to be more specific to today's events
    paginate_by = 5

    def get_queryset(self):
        today = timezone.localdate()
        # Filter for events happening today that are still upcoming
        queryset = Event.objects.filter(
            date=today,
            time__gte=timezone.localtime(timezone.now()).time()
        ).order_by('time').select_related('category')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate() # Get today's date
        now = timezone.now() # Get current datetime

        # Calculate dashboard statistics
        total_events = Event.objects.count()
        
        # Filter for past and upcoming events
        past_events = Event.objects.filter(date__lt=today).count()
        upcoming_events = Event.objects.filter(date__gt=today).count()
        # For events whose date is today, check if their time has passed
        events_today_past = Event.objects.filter(date=today, time__lt=now.time()).count()
        events_today_upcoming = Event.objects.filter(date=today, time__gte=now.time()).count()

        # Add today's events that are still upcoming to the upcoming count
        # and today's events that are past to the past count
        upcoming_events += events_today_upcoming
        past_events += events_today_past

        context['total_events'] = total_events
        context['past_events'] = past_events
        context['upcoming_events'] = upcoming_events
        context['current_date'] = today # To display 'Today's Events'
        return context

# --- Participant CRUD Views (REMOVED) ---
# The Participant model has been replaced by the Django User model.
# All Participant-related views are removed from here.
# User authentication and management will be handled separately.