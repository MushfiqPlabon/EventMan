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
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm # Importing forms
from django.db.models import Q, Sum, Count # For filtering and aggregating
from django.utils import timezone # Django's timezone utilities
from datetime import date # For date-only comparisons


# --- Home View ---
def home(request):
    # Get upcoming 5 events in the project's local timezone
    # Convert timezone.now() to a date for comparison with Event.date
    upcoming_events = Event.objects.filter(
        Q(date__gt=timezone.localdate()) |
        Q(date=timezone.localdate(), time__gte=timezone.localtime(timezone.now()).time())
    ).order_by('date', 'time')[:5].select_related('category') # Optimize by selecting category

    # Aggregate query: Calculate total participants across all events
    total_participants = Participant.objects.aggregate(total=Count('id', distinct=True))['total'] or 0

    return render(request, 'events/home.html', {
        'message': 'Welcome to the Event Management System!',
        'upcoming_events': upcoming_events,
        'total_participants_overall': total_participants,
    })


# --- Event CRUD Views ---

class DashboardView(ListView):
    template_name = 'events/dashboard.html'
    context_object_name = 'today_events'

    def get_queryset(self):
        # This queryset will only fetch today's events for the table
        today = timezone.localdate() # Get today's date in the project's current timezone
        # Add select_related for category to avoid N+1 queries in the today_events table
        queryset = Event.objects.filter(date=today).select_related('category').order_by('time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate() # Get today's date in the project's current timezone
        now_time = timezone.localtime(timezone.now()).time() # Get current time in project's timezone

        # --- Optimized Calculations for Dashboard Stats ---
        context['total_events'] = Event.objects.count()

        # Count distinct participants across all registrations
        context['total_participants'] = Participant.objects.aggregate(total=Count('id', distinct=True))['total'] or 0

        # Past Events: Events where date is before today, OR date is today AND time is before now_time
        context['past_events'] = Event.objects.filter(
            Q(date__lt=today) | Q(date=today, time__lt=now_time)
        ).count()

        # Upcoming Events: Events where date is after today, OR date is today AND time is from now_time onwards
        context['upcoming_events'] = Event.objects.filter(
            Q(date__gt=today) | Q(date=today, time__gte=now_time)
        ).count()

        context['current_date'] = today
        context['current_time'] = now_time

        return context


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.select_related('category')

        # --- Filtering by Category ---
        category_name = self.request.GET.get('category')
        if category_name:
            queryset = queryset.filter(category__name=category_name)

        # --- Filtering by Date Range ---
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass # Handle invalid date format silently or with a message

        if end_date_str:
            try:
                end_date = date.fromisoformat(end_date_str)
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        # --- Search by Name or Location ---
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )
        queryset = queryset.annotate(participant_count=Count('participants'))

        return queryset

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related('participants')

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    # fields = ['name', 'date', 'time', 'location', 'description', 'category'] # REMOVED: form_class takes precedence
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('dashboard') # Redirect to dashboard after creation

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    # fields = ['name', 'date', 'time', 'location', 'description', 'category'] # REMOVED: form_class takes precedence
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('dashboard')

class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    context_object_name = 'event'
    success_url = reverse_lazy('dashboard')


# --- Category CRUD Views ---
class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'events/category_detail.html'
    context_object_name = 'category'

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    # fields = ['name'] # REMOVED: form_class takes precedence
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    # fields = ['name'] # REMOVED: form_class takes precedence
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'events/category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category_list')


# --- Participant CRUD Views ---
class ParticipantListView(ListView):
    model = Participant
    template_name = 'events/participant_list.html'
    context_object_name = 'participants'
    paginate_by = 10

    def get_queryset(self):
        # Corrected from 'registered_events' to 'events'
        return super().get_queryset().prefetch_related('events')

class ParticipantDetailView(DetailView):
    model = Participant
    template_name = 'events/participant_detail.html'
    context_object_name = 'participant'

    def get_queryset(self):
        # Corrected from 'registered_events' to 'events'
        return super().get_queryset().prefetch_related('events')

class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    # fields = ['name', 'email', 'registered_events'] # REMOVED: form_class takes precedence and 'events' is excluded in form
    template_name = 'events/participant_form.html'
    success_url = reverse_lazy('participant_list')

class ParticipantUpdateView(UpdateView):
    model = Participant
    form_class = ParticipantForm
    # fields = ['name', 'email', 'registered_events'] # REMOVED: form_class takes precedence and 'events' is excluded in form
    template_name = 'events/participant_form.html'
    success_url = reverse_lazy('participant_list')

class ParticipantDeleteView(DeleteView):
    model = Participant
    template_name = 'events/participant_confirm_delete.html'
    context_object_name = 'participant'
    success_url = reverse_lazy('participant_list')