"""
Management command to run the Django application with Uvicorn ASGI server.
Provides better performance and concurrency than the default development server.
"""

import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the Django application with Uvicorn ASGI server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            type=str,
            default="127.0.0.1",
            help="Host to bind to (default: 127.0.0.1)",
        )
        parser.add_argument(
            "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
        )
        parser.add_argument(
            "--reload",
            action="store_true",
            help="Enable auto-reload on code changes (development only)",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Number of worker processes (production recommended: 2-4)",
        )

    def handle(self, *args, **options):
        try:
            import uvicorn
        except ImportError:
            self.stderr.write(
                self.style.ERROR(
                    "uvicorn is not installed. Please run: pip install uvicorn"
                )
            )
            sys.exit(1)

        # Uvicorn's reloader requires the application to be passed as a string
        # in the format "module:attribute". We transform the project's setting
        # to match this format just before passing it to the server.
        try:
            parts = settings.ASGI_APPLICATION.rsplit(".", 1)
            app_string_for_uvicorn = ":".join(parts)
        except (ValueError, IndexError):
            # Fallback for unexpected format
            app_string_for_uvicorn = settings.ASGI_APPLICATION

        # Prepare Uvicorn configuration
        uvicorn_config = {
            "app": app_string_for_uvicorn,  # Pass the transformed string
            "host": options["host"],
            "port": options["port"],
            "workers": options["workers"],
        }

        # Add reload option if specified
        if options["reload"]:
            if not settings.DEBUG:
                self.stdout.write(
                    self.style.WARNING(
                        "WARNING: Running with --reload in a non-DEBUG environment is not recommended."
                    )
                )
            uvicorn_config["reload"] = True

        # Print startup info
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Uvicorn server on {options["host"]}:{options["port"]}...'
            )
        )
        self.stdout.write(f"Using ASGI application: {settings.ASGI_APPLICATION}")

        # Run Uvicorn
        uvicorn.run(**uvicorn_config)
