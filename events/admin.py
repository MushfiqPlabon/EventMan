from django.contrib import admin
from .models import Category, Event, Profile # Import your models

# Register your models here.

admin.site.register(Category)
admin.site.register(Event)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    list_filter = ()
    search_fields = ('user__username', 'phone_number')

admin.site.register(Profile, ProfileAdmin)