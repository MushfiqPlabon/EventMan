"""
Category-specific CRUD views using django-extra-views.
"""

from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from ..decorators import organizer_or_admin_required
from ..forms import CategoryForm
from ..models import Category
from ..utils.messages import MessageService
from .generic_django_extra_views import (GenericCreateView, GenericDeleteView,
                                         GenericUpdateView)


@method_decorator(organizer_or_admin_required, name="dispatch")
class CategoryCreateView(GenericCreateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = MessageService.CATEGORY_CREATED_SUCCESS
    error_prefix = "creating category"


def category_list(request):
    """Lists all categories."""
    categories = Category.objects.all().order_by("name")
    return render(request, "events/category_list.html", {"categories": categories})


@method_decorator(organizer_or_admin_required, name="dispatch")
class CategoryUpdateView(GenericUpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = MessageService.CATEGORY_UPDATED_SUCCESS
    error_prefix = "updating category"


@method_decorator(organizer_or_admin_required, name="dispatch")
class CategoryDeleteView(GenericDeleteView):
    model = Category
    template_name = "events/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")
    success_message = MessageService.CATEGORY_DELETED_SUCCESS
