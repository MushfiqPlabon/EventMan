"""
Message constants and formatting service for consistent user-facing messages.
"""


class MessageService:
    """Service class to handle all user-facing messages - follows SRP."""

    # Message constants
    EVENT_CREATED_SUCCESS = "Event created successfully!"
    EVENT_UPDATED_SUCCESS = "Event updated successfully!"
    EVENT_DELETED_SUCCESS = "Event deleted successfully!"
    CATEGORY_CREATED_SUCCESS = "Category created successfully!"
    CATEGORY_UPDATED_SUCCESS = "Category updated successfully!"
    CATEGORY_DELETED_SUCCESS = "Category deleted successfully!"
    UNAUTHORIZED_EDIT_ERROR = "You are not authorized to edit this event."
    UNAUTHORIZED_DELETE_ERROR = "You are not authorized to delete this event."
    OBJECT_NOT_FOUND_ERROR = "Event not found."
    CATEGORY_NOT_FOUND_ERROR = "Category not found."
    ERROR_OCCURRED_ERROR = "Sorry, an error occurred. Please try again."
    RSVP_SUCCESS = 'You have successfully RSVP\'d to "{event_name}"!'
    RSVP_INFO = 'You have un-RSVP\'d from "{event_name}".'
    VERIFICATION_EMAIL_SENT = "Verification email has been sent to your email address."
    VERIFICATION_ERROR = "No email address found for verification."
    EMAIL_ERROR = "Error sending verification email: {error_msg}"
    RSVP_CANCEL_SUCCESS = (
        'You have successfully cancelled your RSVP for "{event_name}".'
    )
    RSVP_CANCEL_DETAILS = (
        "Cancelled RSVP for '{event_name}'. Hope to see you at future events!"
    )

    @classmethod
    def format_rsvp_success(cls, event_name):
        return cls.RSVP_SUCCESS.format(event_name=event_name)

    @classmethod
    def format_rsvp_info(cls, event_name):
        return cls.RSVP_INFO.format(event_name=event_name)

    @classmethod
    def format_email_error(cls, error_msg):
        return cls.EMAIL_ERROR.format(error_msg=error_msg)

    @classmethod
    def format_rsvp_cancel_success(cls, event_name):
        return cls.RSVP_CANCEL_SUCCESS.format(event_name=event_name)

    @classmethod
    def format_rsvp_cancel_details(cls, event_name):
        return cls.RSVP_CANCEL_DETAILS.format(event_name=event_name)
