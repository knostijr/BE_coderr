"""User model for authentication and profiles.

This module defines the custom User model extending Django's AbstractUser
with additional fields for business/customer types and profile information.
"""

# Third-party imports
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with type and profile fields.
    
    Extends Django's AbstractUser to add:
    - User type (customer or business)
    - Profile fields (location, tel, description, working_hours)
    - Timestamps
    
    Attributes:
        type (str): User type - 'customer' or 'business'
        location (str): User's location
        tel (str): Telephone number
        description (str): User description/bio
        working_hours (str): Working hours information
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]
    
    type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    
    # Profile fields
    location = models.CharField(max_length=200, blank=True)
    tel = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        """Return string representation of user.
        
        Returns:
            str: Username of the user
        """
        return self.username