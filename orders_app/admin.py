"""Admin configuration for orders app."""

# Third-party imports
from django.contrib import admin

# Local imports
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""

    list_display = ['id', 'customer_user', 'business_user', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['customer_user__username', 'business_user__username']