"""
Generic CRUD views using django-extra-views to replace custom implementations.
"""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView

from ..decorators import organizer_or_admin_required
from ..utils.error_handler import ErrorHandlerService, FormErrorHandler


@method_decorator(organizer_or_admin_required, name="dispatch")
class GenericCreateView(CreateView):
    """Generic Create View using django-extra-views."""

    def form_valid(self, form):
        obj = form.save(commit=False)
        # Add organizer if model has organizer field
        if hasattr(obj, "organizer") and hasattr(self.request, "user"):
            obj.organizer = self.request.user
        obj.save()

        success, error_response = ErrorHandlerService.validate_and_handle(
            obj,
            success_message=getattr(
                self, "success_message", "Item created successfully"
            ),
            error_prefix=getattr(self, "error_prefix", "creating item"),
        )

        if not success:
            messages.error(self.request, f"Error: {error_response}")
            return self.form_invalid(form)

        messages.success(
            self.request, getattr(self, "success_message", "Item created successfully")
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        FormErrorHandler.handle_form_errors(
            self.request, form, getattr(self, "error_prefix", "creating item")
        )
        return super().form_invalid(form)


@method_decorator(organizer_or_admin_required, name="dispatch")
class GenericUpdateView(UpdateView):
    """Generic Update View using django-extra-views."""

    def form_valid(self, form):
        obj = form.save(commit=False)

        success, error_response = ErrorHandlerService.validate_and_handle(
            obj,
            success_message=getattr(
                self, "success_message", "Item updated successfully"
            ),
            error_prefix=getattr(self, "error_prefix", "updating item"),
        )

        if not success:
            messages.error(self.request, f"Error: {error_response}")
            return self.form_invalid(form)

        response = super().form_valid(form)
        messages.success(
            self.request, getattr(self, "success_message", "Item updated successfully")
        )
        return response

    def form_invalid(self, form):
        FormErrorHandler.handle_form_errors(
            self.request, form, getattr(self, "error_prefix", "updating item")
        )
        return super().form_invalid(form)


@method_decorator(organizer_or_admin_required, name="dispatch")
class GenericDeleteView(DeleteView):
    """Generic Delete View using django's built-in functionality."""

    def delete(self, request, *args, **kwargs):
        self.get_object()
        success_message = getattr(self, "success_message", "Item deleted successfully")

        response = super().delete(request, *args, **kwargs)
        messages.success(request, success_message)
        return response
