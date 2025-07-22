from django.contrib import admin
from .models import Category, Event # Import your models

# Register your models here.

admin.site.register(Category)
admin.site.register(Event)