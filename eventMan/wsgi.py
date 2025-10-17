"""
WSGI config for EventMan project.
Optimized for Vercel deployment.
"""

import os

from django.core.wsgi import get_wsgi_application

# Set default settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eventMan.settings")

application = get_wsgi_application()

# Vercel serverless function handler
app = application
