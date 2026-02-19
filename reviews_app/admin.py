"""Admin configuration for reviews app."""

# Third-party imports
from django.contrib import admin

# Local imports
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model."""

    list_display = ['id', 'business_user', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['business_user__username', 'reviewer__username']