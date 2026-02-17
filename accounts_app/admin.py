"""Admin configuration for accounts_app."""

# Third-party
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Local
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""

    list_display = ['username', 'email', 'type', 'first_name', 'last_name']
    list_filter = ['type', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('type', 'file', 'location', 'tel', 'description', 'working_hours')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )