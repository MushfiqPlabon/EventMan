from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from .decorators import admin_required, organizer_required, participant_required, organizer_or_admin_required, is_organizer, is_participant
from .models import Event, Category, Profile
from .forms import EventForm, CategoryForm, UserUpdateForm, ProfileUpdateForm, PasswordChangeForm
from django.dispatch import receiver # Import receiver for signals
from django.db.models.signals import m2m_changed # Import m2m_changed signal
from django.core.mail import send_mail # Import send_mail for emails
from django.template.loader import render_to_string # For rendering email templates
from django.utils.html import strip_tags # For plain text email content
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView as AuthPasswordChangeView
from django.contrib.auth.models import Group # Import Group model
from django.contrib.auth import get_user_model

User = get_user_model() # Get the active User model

class HomeView(TemplateView):
    template_name = 'home.html'

@method_decorator(login_required, name='dispatch')
class DashboardRedirectView(View):
    """Redirects users to their specific dashboard based on their role."""
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif is_organizer(request.user):
            return redirect('organizer_dashboard')
        elif is_participant(request.user):
            return redirect('participant_dashboard')
        return render(request, 'dashboard_base.html', {'message': 'Welcome to your general dashboard!'})


@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(TemplateView):
    """Admin Dashboard view."""
    template_name = 'dashboards/admin_dashboard.html'

@method_decorator(organizer_required, name='dispatch')
class OrganizerDashboardView(TemplateView):
    """Organizer Dashboard view with stats and today's events."""
    template_name = 'dashboards/organizer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Stats Grid Data
        # Filter events by the current logged-in organizer
        organizer_events = Event.objects.filter(organizer=self.request.user)

        total_events = organizer_events.count()
        upcoming_events = organizer_events.filter(date__gte=today).count()
        past_events = organizer_events.filter(date__lt=today).count()
        
        # Total participants for events organized by the current user
        total_participants = organizer_events.aggregate(total_users=Count('participants', distinct=True))['total_users']

        # Today's Events Listing for the current organizer
        today_events = organizer_events.filter(date=today).order_by('time')

        context.update({
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'total_participants': total_participants if total_participants is not None else 0, # Handle None if no participants
            'today_events': today_events,
            'current_date': today,
            'current_time': timezone.now(),
        })
        return context

@method_decorator(participant_required, name='dispatch') # Only participants can RSVP
class ParticipantDashboardView(TemplateView):
    """Participant Dashboard view, showing RSVP'd events."""
    template_name = 'dashboards/participant_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch events the current user has RSVP'd to
        rsvp_events = self.request.user.events_joined.all().select_related('category').order_by('date', 'time')
        context['rsvp_events'] = rsvp_events
        return context

@method_decorator(admin_required, name='dispatch')
class ParticipantListView(ListView):
    model = User
    template_name = 'events/participant_list.html' # You'll need to create this template
    context_object_name = 'participants'

    def get_queryset(self):
        # Filter for users who are in the 'Participant' group
        return User.objects.filter(groups__name='Participant').order_by('username')

class EventListView(ListView):
    """
    Lists all events, with search and filtering capabilities.
    Search by event name or location.
    Filter by category, upcoming, or past.
    """
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10 # Optional: Add pagination

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related('participants').order_by('date', 'time')

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            )

        # Filtering by event status (upcoming, past)
        filter_status = self.request.GET.get('status')
        today = timezone.now().date()
        if filter_status == 'upcoming':
            queryset = queryset.filter(date__gte=today)
        elif filter_status == 'past':
            queryset = queryset.filter(date__lt=today)

        # Filtering by category
        filter_category = self.request.GET.get('category')
        if filter_category:
            queryset = queryset.filter(category__name__iexact=filter_category) # Case-insensitive category match

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_query'] = self.request.GET.get('q')
        context['current_status'] = self.request.GET.get('status')
        context['current_category'] = self.request.GET.get('category')
        return context

class EventDetailView(DetailView):
    """Displays detailed information for a single event."""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related('participants')


@method_decorator(organizer_or_admin_required, name='dispatch')
class EventCreateView(CreateView):
    """Allows Organizers and Admins to create new events."""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Event'
        return context

    def form_valid(self, form):
        form.instance.organizer = self.request.user # Assign the current user as the organizer
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating event. Please check your input.')
        return super().form_invalid(form)

    def get_success_url(self):
        return redirect('event_detail', pk=self.object.pk).url

@method_decorator(organizer_or_admin_required, name='dispatch')
class EventUpdateView(UpdateView):
    """Allows Organizers and Admins to update existing events."""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Event'
        context['event'] = self.get_object()
        return context

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if not request.user.is_superuser and event.organizer != request.user:
            messages.error(request, 'You are not authorized to edit this event.')
            return redirect('event_detail', pk=event.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating event. Please check your input.')
        return super().form_invalid(form)

    def get_success_url(self):
        return redirect('event_detail', pk=self.object.pk).url

@method_decorator(organizer_or_admin_required, name='dispatch')
class EventDeleteView(DeleteView):
    """Allows Organizers and Admins to delete events."""
    model = Event
    template_name = 'events/event_confirm_delete.html'
    context_object_name = 'event'

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if not request.user.is_superuser and event.organizer != request.user:
            messages.error(request, 'You are not authorized to delete this event.')
            return redirect('event_detail', pk=event.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Event deleted successfully!')
        return reverse_lazy('event_list')

@method_decorator(login_required, name='dispatch') # User must be logged in to RSVP
class RSVPToggleView(View):
    """Toggles a user's RSVP status for an event."""
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if event.participants.filter(pk=user.pk).exists():
            event.participants.remove(user)
            messages.info(request, f'You have un-RSVP\'d from "{event.name}".')
        else:
            event.participants.add(user)
            messages.success(request, f'You have successfully RSVP\'d to "{event.name}"!')
            # Signal will handle sending the email
        return redirect('event_detail', pk=event.pk)

    def get(self, request, pk):
        return redirect('event_detail', pk=pk) # Redirect if not a POST request


@method_decorator(organizer_or_admin_required, name='dispatch')
class CategoryCreateView(CreateView):
    """Allows Organizers and Admins to create new categories."""
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Category'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating category. Please check your input.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('category_list')

class CategoryListView(ListView):
    """Lists all categories."""
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.all().order_by('name')

@method_decorator(organizer_or_admin_required, name='dispatch')
class CategoryUpdateView(UpdateView):
    """Allows Organizers and Admins to update existing categories."""
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Category'
        context['category'] = self.get_object()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating category. Please check your input.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('category_list')

@method_decorator(organizer_or_admin_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    """Allows Organizers and Admins to delete categories."""
    model = Category
    template_name = 'events/category_confirm_delete.html'
    context_object_name = 'category'

    def get_success_url(self):
        messages.success(self.request, 'Category deleted successfully!')
        return reverse_lazy('category_list')

@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'account/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    template_name = 'account/profile_update.html'

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating your profile. Please check your input.')
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class PasswordChangeView(AuthPasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'account/password_change.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)

class PasswordChangeDoneView(TemplateView):
    template_name = 'account/password_change_done.html'