"""Admin configuration for orders_app."""

# Third-party
from django.contrib import admin

# Local
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""

    list_display = ['id', 'customer_user', 'business_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_user__username', 'business_user__username']