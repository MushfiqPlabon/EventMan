"""
Constants for EventMan application.
Centralized configuration to maintain DRY principle.
"""


# User Groups - Centralized definition to avoid inconsistencies
class UserGroups:
    ADMIN = "Admin"
    ORGANIZER = "Organizer"
    PARTICIPANT = "Participant"


# Email Configuration
DEFAULT_NOREPLY_EMAIL = "noreply@eventman.com"

# Cache Configuration
CACHE_TIMEOUTS = {
    "DASHBOARD_STATS": 300,  # 5 minutes
    "SEARCH_RESULTS": 600,  # 10 minutes
    "EVENT_VIEWS": 86400,  # 24 hours
}

# Payment Status Choices
PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("valid", "Valid"),
    ("failed", "Failed"),
]

# RSVP Status Choices
RSVP_STATUS_CHOICES = [
    ("attending", "Attending"),
    ("not_attending", "Not Attending"),
    ("maybe", "Maybe"),
]
