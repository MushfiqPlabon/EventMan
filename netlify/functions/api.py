import os

import django
from django.core.asgi import get_asgi_application
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eventMan.settings")
django.setup()

app = get_asgi_application()
handler = Mangum(app, lifespan="off")
