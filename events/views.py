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
from django.db.models import Q, Sum # For filtering and aggregating

# --- Home View ---
def home(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date', 'time')[:5]
    # Aggregate query: Calculate total participants across all events
    total_participants = Participant.objects.count() # This counts unique participant records
    # If you wanted total registrations for events (where one participant might register for multiple events),
    # you would do: Event.objects.aggregate(total_regs=Sum('participants__id'))['total_regs'] or similar,
    # but counting unique participant entries is usually what's meant by "total participants".

    return render(request, 'events/home.html', {
        'message': 'Welcome to the Event Management System!',
        'upcoming_events': upcoming_events,
        'total_participants_overall': total_participants, # Pass to context
    })

# --- Event CRUD Views ---

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').order_by('date', 'time')

        # --- Filtering by Category ---
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        # --- Filtering by Date Range ---
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                # Handle invalid date format if necessary, e.g., pass an error message
                pass

        if end_date_str:
            try:
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        # --- Search by Name or Location ---
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name') # Pass all categories for filter dropdown
        context['selected_category'] = self.request.GET.get('category', '') # To pre-select dropdown
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class EventDetailView(DetailView):
    """
    Displays detailed information for a single event.
    Optimized with prefetch_related to fetch related Participant data.
    """
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        # Optimizing query: Use prefetch_related to fetch all associated Participants
        # This avoids N+1 queries if you iterate through event.participants.all
        queryset = super().get_queryset().prefetch_related('participants')
        return queryset

class EventCreateView(CreateView):
    """
    Handles the creation of a new event.
    Uses EventForm.
    """
    model = Event
    form_class = EventForm # Use the form we just created
    template_name = 'events/event_form.html' # Re-use form template for create and update
    success_url = reverse_lazy('event_list') # Redirect to event list after successful creation

class EventUpdateView(UpdateView):
    """
    Handles the updating of an existing event.
    Uses EventForm and pre-fills the form with existing data.
    """
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    context_object_name = 'event' # Passes the object to the template
    success_url = reverse_lazy('event_list') # Redirect to event list after successful update

class EventDeleteView(DeleteView):
    """
    Handles the deletion of an event.
    Displays a confirmation page before deleting.
    """
    model = Event
    template_name = 'events/event_confirm_delete.html' # Dedicated confirm delete template
    context_object_name = 'event' # Passes the object to the template
    success_url = reverse_lazy('event_list') # Redirect to event list after successful deletion

# --- Category CRUD Views ---

class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10 # Optional

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


# --- Participant CRUD Views ---

class ParticipantListView(ListView):
    model = Participant
    template_name = 'events/participant_list.html'
    context_object_name = 'participants'
    paginate_by = 10 # Optional

class ParticipantDetailView(DetailView):
    model = Participant
    template_name = 'events/participant_detail.html'
    context_object_name = 'participant'
    # Optional: If you want to show events a participant is linked to,
    # you'd use prefetch_related('events') here, but this form currently
    # doesn't manage the 'events' field. For simplicity, we'll omit it.
    # def get_queryset(self):
    #     return super().get_queryset().prefetch_related('events')


class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/participant_form.html'
    success_url = reverse_lazy('participant_list')

class ParticipantUpdateView(UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'events/participant_form.html'
    context_object_name = 'participant'
    success_url = reverse_lazy('participant_list')

class ParticipantDeleteView(DeleteView):
    model = Participant
    template_name = 'events/participant_confirm_delete.html'
    context_object_name = 'participant'
    success_url = reverse_lazy('participant_list')

# Import timezone for the home view if not already there
from django.utils import timezone