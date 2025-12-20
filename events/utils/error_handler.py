"""
Error handling utilities for the EventMan application.
Provides centralized, standardized error handling for better maintainability.
"""

import logging
from functools import wraps

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class ErrorHandlerService:
    """
    Centralized error handling service that provides standardized
    error responses and logging throughout the application.
    """

    @staticmethod
    def handle_view_exception(
        request, exception, context="", fallback_url="event_list"
    ):
        """
        Handle exceptions in views with standardized error messages.

        Args:
            request: The HTTP request object
            exception: The exception that occurred
            context: Additional context about where the error occurred
            fallback_url: URL to redirect to if no referer is available

        Returns:
            HttpResponseRedirect to appropriate route
        """
        # Log the error with additional context to help with debugging
        logger.error(
            f"Error in {context or 'unknown view'}: {type(exception).__name__} - {str(exception)}",
            extra={
                "request": request,
                "user_id": getattr(request.user, "id", "anonymous"),
            },
        )

        # Map specific exception types to user-friendly messages
        error_map = {
            ValidationError.__name__: "Invalid data provided. Please check your input and try again.",
            PermissionError.__name__: "You don't have permission to perform this action.",
            ValueError.__name__: "Invalid value provided. Please check your input and try again.",
            TypeError.__name__: "Incorrect data type provided. Please check your input and try again.",
        }

        # Determine user-friendly error message
        error_type = type(exception).__name__
        user_message = error_map.get(
            error_type, "An unexpected error occurred. Please try again."
        )

        # Add additional context to the message if provided
        if context:
            user_message = f"Error in {context}: {user_message}"

        # Add error message to Django messages framework
        messages.error(request, user_message)

        # Determine where to redirect the user
        referer = request.META.get("HTTP_REFERER")
        if referer and request.build_absolute_uri("/") in referer:
            return redirect(referer)
        else:
            return redirect(fallback_url)

    @staticmethod
    def handle_api_exception(exception, context=""):
        """
        Handle exceptions for API endpoints and return JSON responses.

        Args:
            exception: The exception that occurred
            context: Additional context about where the error occurred

        Returns:
            JsonResponse with error details
        """
        # Log the error with additional context
        logger.error(f"API Error in {context or 'unknown endpoint'}: {str(exception)}")

        # Determine appropriate error message
        if isinstance(exception, ValidationError):
            message = "Invalid data provided."
        else:
            message = "An unexpected error occurred."

        return JsonResponse(
            {"success": False, "error": message, "details": str(exception)}, status=500
        )

    @staticmethod
    def _format_validation_errors(e):
        """Format validation errors into a user-friendly string."""
        if hasattr(e, "message_dict"):
            error_messages = []
            for field, errors in e.message_dict.items():
                for error in errors:
                    error_messages.append(f"{field.replace('_', ' ').title()}: {error}")
            error_str = " ".join(error_messages)
        else:
            error_str = str(e)

        return error_str

    @staticmethod
    def _handle_unexpected_error(e, error_prefix):
        """Handle unexpected errors during model validation."""
        logger.error(f"Unexpected error during model validation: {str(e)}")
        return f"{error_prefix} Unexpected error occurred: {str(e)}"

    @staticmethod
    def validate_and_handle(model_instance, success_message="", error_prefix=""):
        """
        Validate a model instance and handle errors appropriately.

        Args:
            model_instance: The model instance to validate and save
            success_message: Success message to show if validation succeeds
            error_prefix: Prefix for error messages

        Returns:
            Tuple of (success: bool, error_response_or_none)
        """
        try:
            model_instance.full_clean()  # This runs all field and model validations
            model_instance.save()
            # Add success message if provided (requires request context which we don't have here)
            # The caller is responsible for adding messages
            return True, None
        except ValidationError as e:
            error_str = ErrorHandlerService._format_validation_errors(e)
            logger.warning(f"Validation error: {error_str}")
            return False, error_str
        except Exception as e:
            error_response = ErrorHandlerService._handle_unexpected_error(
                e, error_prefix
            )
            return False, error_response

    @staticmethod
    def safe_execute(view_func):
        """
        Decorator to wrap view functions with error handling.

        Args:
            view_func: The view function to wrap

        Returns:
            Wrapped view function with error handling
        """

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except Exception as e:
                return ErrorHandlerService.handle_view_exception(
                    request, e, context=f"{view_func.__module__}.{view_func.__name__}"
                )

        return wrapper


def handle_exceptions(context=""):
    """
    Decorator factory for adding error handling to view functions.

    Args:
        context: Context string to include in error messages

    Returns:
        Decorator that wraps function with error handling
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except Exception as e:
                return ErrorHandlerService.handle_view_exception(
                    request, e, context=context, fallback_url="event_list"
                )

        return wrapper

    return decorator


class FormErrorHandler:
    """
    Helper class for handling form-related errors with user-friendly messages.
    """

    @staticmethod
    def handle_form_errors(request, form, action="processing"):
        """
        Handle form errors with user-friendly messages.

        Args:
            request: The HTTP request object
            form: The form with errors
            action: Action being performed (e.g. "saving", "updating")

        Returns:
            None (adds messages to Django messages framework)
        """
        error_count = len(form.errors)
        if error_count == 1:
            # For a single error, show the specific message
            field_name = list(form.errors.keys())[0] if form.errors else "form"
            field_label = (
                form.fields[field_name].label
                if field_name in form.fields
                else field_name
            )
            error_msg = list(form.errors.values())[0][0]
            messages.error(
                request, f"Error {action} {field_label.lower()}: {error_msg}"
            )
        else:
            # For multiple errors, show a general message with count
            messages.error(
                request,
                f"Error {action} form. {error_count} validation errors occurred. Please check the form and try again.",
            )

        logger.debug(f"Form errors during {action}: {dict(form.errors)}")
