from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, UpdateView, CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin # Import UserPassesTestMixin


User = get_user_model()

# Create your views here.

# Test for users
"""
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['userprofile'] = UserProfile.objects.get(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        print("views", user_profile)
        context['form'] = self.form_class(
            instance=self.object, userprofile=user_profile)
        return context

    def form_valid(self, form):
        form.save(commit=True)
        return redirect('profile')
"""


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')


def is_admin(user):
    return user.groups.filter(name='Admin').exists()


class SignUpView(View):
    """
    Class-based view for user registration.
    """
    def get(self, request):
        form = CustomRegistrationForm()
        return render(request, 'registration/register.html', {"form": form})

    def post(self, request):
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
        else:
            print("Form is not valid")
        return render(request, 'registration/register.html', {"form": form})


# The CustomLoginView already exists and is class-based, so no change here.
class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()


class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm


class SignOutView(View):
    """
    Class-based view for user logout.
    """
    @method_decorator(login_required)
    def post(self, request):
        logout(request)
        return redirect('sign-in')


class ActivateUserView(View):
    """
    Class-based view for user account activation via email.
    """
    def get(self, request, user_id, token):
        try:
            user = User.objects.get(id=user_id)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('sign-in')
            else:
                return HttpResponse('Invalid Id or token')
        except User.DoesNotExist:
            return HttpResponse('User not found')


class AdminDashboardView(UserPassesTestMixin, ListView):
    """
    Class-based view for the admin dashboard.
    """
    template_name = 'admin/dashboard.html'
    context_object_name = 'users'

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        users = User.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
        ).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = 'No Group Assigned'
        return users


class AssignRoleView(UserPassesTestMixin, View):
    """
    Class-based view for assigning roles to users.
    """
    template_name = 'admin/assign_role.html'

    def test_func(self):
        return is_admin(self.request.user)

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        form = AssignRoleForm()
        return render(request, self.template_name, {"form": form, "user": user})

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()  # Remove old roles
            user.groups.add(role)
            messages.success(request, f"User {
                             user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')
        return render(request, self.template_name, {"form": form, "user": user})


class CreateGroupView(UserPassesTestMixin, CreateView):
    """
    Class-based view for creating new user groups.
    """
    model = Group
    form_class = CreateGroupForm
    template_name = 'admin/create_group.html'
    success_url = reverse_lazy('create-group')

    def test_func(self):
        return is_admin(self.request.user)

    def form_valid(self, form):
        group = form.save()
        messages.success(self.request, f"Group {
                         group.name} has been created successfully")
        return super().form_valid(form)


class GroupListView(UserPassesTestMixin, ListView):
    """
    Class-based view for listing user groups.
    """
    model = Group
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        return Group.objects.prefetch_related('permissions').all()


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)


"""

    Admin
        - Sobkisui
    Manager
        - project
        - task create
    Employee
        - Task read
        - Task update

    Role Based Access Control (RBAC)
"""