from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"

    def ready(self):
        # Import signals here to ensure they are connected
        import events.signals  # noqa: F401
        import events.user_profile_signals  # noqa: F401

        # Import the signal handler to create default groups
        from . import apps_ready_signals  # noqa: F401
