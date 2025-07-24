from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskModelForm, TaskDetailModelForm
from tasks.models import Task, Project
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView


# Class Based View Re-use example


class Greetings(View):
    greetings = 'Hello Everyone'

    def get(self, request):
        return HttpResponse(self.greetings)


class HiGreetings(Greetings):
    greetings = 'Hi Everyone'


class HiHowGreetings(Greetings):
    greetings = 'Hi Everyone, How are you'


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_employee(user):
    return user.groups.filter(name='Manager').exists()


class ManagerDashboard(UserPassesTestMixin, ListView):
    template_name = "dashboard/manager-dashboard.html"
    context_object_name = "tasks"

    def test_func(self):
        return is_manager(self.request.user)

    def get_queryset(self):
        type = self.request.GET.get('type', 'all')
        base_query = Task.objects.select_related('details').prefetch_related('assigned_to')

        if type == 'completed':
            tasks = base_query.filter(status='COMPLETED')
        elif type == 'in-progress':
            tasks = base_query.filter(status='IN_PROGRESS')
        elif type == 'pending':
            tasks = base_query.filter(status='PENDING')
        elif type == 'all':
            tasks = base_query.all()
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['counts'] = Task.objects.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            pending=Count('id', filter=Q(status='PENDING')),
        )
        context['role'] = 'manager'
        return context


class EmployeeDashboard(UserPassesTestMixin, View):
    template_name = "dashboard/user-dashboard.html"

    def test_func(self):
        return is_employee(self.request.user)

    def get(self, request):
        return render(request, self.template_name)


class CreateTask(LoginRequiredMixin, PermissionRequiredMixin, ContextMixin, View):
    """ For creating task """
    permission_required = 'tasks.add_task'
    login_url = 'no-permission'
    template_name = 'task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = kwargs.get('task_form', TaskModelForm())
        context['task_detail_form'] = kwargs.get(
            'task_detail_form', TaskDetailModelForm())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            context = self.get_context_data(
                task_form=task_form, task_detail_form=task_detail_form)
            return render(request, self.template_name, context)
        context = self.get_context_data(
            task_form=task_form, task_detail_form=task_detail_form)
        return render(request, self.template_name, context)


class UpdateTask(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'
    permission_required = 'tasks.change_task'
    login_url = 'no-permission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        if hasattr(self.object, 'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(
                instance=self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)
        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, 'details', None))

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', self.object.id)
        return render(request, self.template_name, self.get_context_data(task_form=task_form, task_detail_form=task_detail_form))


class DeleteTask(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = 'tasks.delete_task'
    login_url = 'no-permission'
    success_url = 'manager-dashboard'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Task Deleted Successfully')
        return self.delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')


class ViewProject(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'show_task.html'
    permission_required = "projects.view_project"
    login_url = 'no-permission'

    def get_queryset(self):
        queryset = Project.objects.annotate(
            num_task=Count('task')).order_by('num_task')
        return queryset


class TaskDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    permission_required = 'tasks.view_task'
    login_url = 'no-permission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)


@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')

    return redirect('no-permission')