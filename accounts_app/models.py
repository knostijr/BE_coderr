"""User model for accounts_app."""

# Third-party
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with type, profile picture, and profile fields.

    Attributes:
        type (str): 'customer' or 'business'.
        file (ImageField): Profile picture (optional).
        location (str): Location, never null (default='').
        tel (str): Phone number, never null (default='').
        description (str): Bio, never null (default='').
        working_hours (str): Working hours, never null (default='').
        created_at (datetime): Auto-set on creation.
        updated_at (datetime): Auto-set on update.
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
    file = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    location = models.CharField(max_length=200, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        """Return username as string representation."""
        return self.username