import django_filters
from django import forms
from django.db import models
from django.utils import timezone

from .models import Category, Event


class EventFilter(django_filters.FilterSet):
    """Advanced event filtering with HTMX integration"""

    q = django_filters.CharFilter(
        method="search_events",
        widget=forms.TextInput(
            attrs={"placeholder": "Search events...", "class": "form-control"}
        ),
        label="Search",
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    status = django_filters.ChoiceFilter(
        choices=Event.STATUS,
        method="filter_by_status",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    date_from = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="From Date",
    )

    date_to = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="To Date",
    )

    class Meta:
        model = Event
        fields = []

    def search_events(self, queryset, name, value):
        """Custom search across multiple fields"""
        if value:
            return queryset.filter(
                models.Q(name__icontains=value)
                | models.Q(description__icontains=value)
                | models.Q(location__icontains=value)
                | models.Q(category__name__icontains=value)
            )
        return queryset

    def filter_by_status(self, queryset, name, value):
        """Filter events by status (upcoming/past/today)"""
        current_date = timezone.localdate()

        if value == "upcoming":
            return queryset.filter(date__gte=current_date, status="published")
        elif value == "past":
            return queryset.filter(date__lt=current_date)
        elif value == "today":
            return queryset.filter(date=current_date, status="published")

        return queryset.filter(status="published")


class CategoryFilter(django_filters.FilterSet):
    """Category filtering"""

    name = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"placeholder": "Search categories...", "class": "form-control"}
        ),
    )

    class Meta:
        model = Category
        fields = ["name"]
