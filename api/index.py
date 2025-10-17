import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eventMan.wsgi import app as django_application

def handler(environ, start_response):
    return django_application(environ, start_response)