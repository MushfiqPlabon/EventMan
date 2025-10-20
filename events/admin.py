from django.contrib import admin

from .models import RSVP, Category, Event, Payment, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")
    search_fields = ("name", "description")
    list_filter = ("created", "modified")
    readonly_fields = ("created", "modified")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "organizer",
        "date",
        "status",
        "tickets_sold",
        "created",
    )
    list_filter = ("status", "category", "date", "created")
    search_fields = ("name", "description", "location", "organizer__username")
    readonly_fields = ("created", "modified", "tickets_sold")
    filter_horizontal = ("participants",)
    date_hierarchy = "date"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "description", "category", "organizer")},
        ),
        ("Event Details", {"fields": ("date", "time", "location", "image")}),
        ("Pricing & Status", {"fields": ("ticket_price", "status", "tickets_sold")}),
        ("Participants", {"fields": ("participants",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user", "event", "amount", "status", "created")
    list_filter = ("status", "created")
    search_fields = ("transaction_id", "user__username", "event__name")
    readonly_fields = ("created", "modified")
    date_hierarchy = "created"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "created")
    list_filter = ("created", "modified")
    search_fields = ("user__username", "user__email", "phone_number")
    readonly_fields = ("created", "modified")


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "created")
    list_filter = ("status", "created")
    search_fields = ("user__username", "event__name")
    readonly_fields = ("created", "modified")
    date_hierarchy = "created"


# Customize admin site
admin.site.site_header = "EventMan Administration"
admin.site.site_title = "EventMan Admin"
admin.site.index_title = "Welcome to EventMan Administration"
