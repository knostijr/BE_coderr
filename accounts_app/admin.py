"""Admin configuration for accounts app.

Registers User model with custom admin interface.
"""

# Third-party imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Local imports
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for User model.
    
    Extends Django's default UserAdmin with custom fields for
    user type and profile information.
    """
    
    list_display = [
        'username',
        'email',
        'type',
        'first_name',
        'last_name',
        'created_at'
    ]
    list_filter = ['type', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('type', 'location', 'tel', 'description', 'working_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']