from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from .decorators import admin_required, organizer_required, participant_required, organizer_or_admin_required
from .models import Event, Category
from .forms import EventForm, CategoryForm
from django.dispatch import receiver # Import receiver for signals
from django.db.models.signals import m2m_changed # Import m2m_changed signal
from django.core.mail import send_mail # Import send_mail for emails
from django.template.loader import render_to_string # For rendering email templates
from django.utils.html import strip_tags # For plain text email content

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard_redirect(request):
    """Redirects users to their specific dashboard based on their role."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    elif request.user.groups.filter(name='Participant').exists():
        return redirect('participant_dashboard')
    return render(request, 'dashboard_base.html', {'message': 'Welcome to your general dashboard!'})


@admin_required
def admin_dashboard(request):
    """Admin Dashboard view."""
    return render(request, 'dashboards/admin_dashboard.html')

@organizer_required
def organizer_dashboard(request):
    """Organizer Dashboard view with stats and today's events."""
    today = timezone.now().date()

    # Stats Grid Data
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gte=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    # Total participants across all events (using aggregation)
    # This counts distinct users who are participants in any event
    total_participants = Event.objects.aggregate(total_users=Count('participants', distinct=True))['total_users']

    # Today's Events Listing
    today_events = Event.objects.filter(date=today).order_by('time')

    context = {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_participants': total_participants if total_participants is not None else 0, # Handle None if no participants
        'today_events': today_events,
    }
    return render(request, 'dashboards/organizer_dashboard.html', context)

@participant_required # Only participants can RSVP
def participant_dashboard(request):
    """Participant Dashboard view, showing RSVP'd events."""
    # Fetch events the current user has RSVP'd to
    rsvp_events = request.user.events_joined.all().order_by('date', 'time')
    context = {
        'rsvp_events': rsvp_events
    }
    return render(request, 'dashboards/participant_dashboard.html', context)

def event_list(request):
    """
    Lists all events, with search and filtering capabilities.
    Search by event name or location.
    Filter by category, upcoming, or past.
    """
    events = Event.objects.select_related('category').prefetch_related('participants').order_by('date', 'time')
    categories = Category.objects.all()

    # Search functionality
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    # Filtering by event status (upcoming, past)
    filter_status = request.GET.get('status')
    today = timezone.now().date()
    if filter_status == 'upcoming':
        events = events.filter(date__gte=today)
    elif filter_status == 'past':
        events = events.filter(date__lt=today)

    # Filtering by category
    filter_category = request.GET.get('category')
    if filter_category:
        events = events.filter(category__name__iexact=filter_category) # Case-insensitive category match

    context = {
        'events': events,
        'categories': categories,
        'current_query': query,
        'current_status': filter_status,
        'current_category': filter_category,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, pk):
    """Displays detailed information for a single event."""
    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('participants'), pk=pk)
    context = {
        'event': event
    }
    return render(request, 'events/event_detail.html', context)


@organizer_or_admin_required
def event_create(request):
    """Allows Organizers and Admins to create new events."""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user # Assign the current user as the organizer
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Error creating event. Please check your input.')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

@organizer_or_admin_required
def event_update(request, pk):
    """Allows Organizers and Admins to update existing events."""
    event = get_object_or_404(Event, pk=pk)
    # Ensure only the organizer or an admin can edit the event
    if not request.user.is_superuser and event.organizer != request.user:
        messages.error(request, 'You are not authorized to edit this event.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Error updating event. Please check your input.')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Update Event', 'event': event})

@organizer_or_admin_required
def event_delete(request, pk):
    """Allows Organizers and Admins to delete events."""
    event = get_object_or_404(Event, pk=pk)
    # Ensure only the organizer or an admin can delete the event
    if not request.user.is_superuser and event.organizer != request.user:
        messages.error(request, 'You are not authorized to delete this event.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list') # Redirect to event list after deletion
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required # User must be logged in to RSVP
def rsvp_toggle(request, pk):
    """Toggles a user's RSVP status for an event."""
    event = get_object_or_404(Event, pk=pk)
    user = request.user

    if request.method == 'POST':
        if user in event.participants.all():
            event.participants.remove(user)
            messages.info(request, f'You have un-RSVP\'d from "{event.name}".')
        else:
            event.participants.add(user)
            messages.success(request, f'You have successfully RSVP\'d to "{event.name}"!')
            # Signal will handle sending the email
        return redirect('event_detail', pk=event.pk)
    return redirect('event_detail', pk=event.pk) # Redirect if not a POST request

@organizer_or_admin_required
def category_create(request):
    """Allows Organizers and Admins to create new categories."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list') # Redirect to category list
        else:
            messages.error(request, 'Error creating category. Please check your input.')
    else:
        form = CategoryForm()
    return render(request, 'events/category_form.html', {'form': form, 'title': 'Create Category'})

def category_list(request):
    """Lists all categories."""
    categories = Category.objects.all().order_by('name')
    return render(request, 'events/category_list.html', {'categories': categories})

@organizer_or_admin_required
def category_update(request, pk):
    """Allows Organizers and Admins to update existing categories."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
        else:
            messages.error(request, 'Error updating category. Please check your input.')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'events/category_form.html', {'form': form, 'title': 'Update Category', 'category': category})

@organizer_or_admin_required
def category_delete(request, pk):
    """Allows Organizers and Admins to delete categories."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    return render(request, 'events/category_confirm_delete.html', {'category': category})