"""User model for accounts app."""

# Third-party imports
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with type and profile fields.

    Attributes:
        type (str): User type - 'customer' or 'business'.
        file (ImageField): Optional profile picture.
        location (str): User location, defaults to empty string.
        tel (str): Phone number, defaults to empty string.
        description (str): Profile description, defaults to empty string.
        working_hours (str): Working hours info, defaults to empty string.
        created_at (datetime): Account creation timestamp.
        updated_at (datetime): Last update timestamp (internal use only).
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
        """Return username as string representation.

        Returns:
            str: The username.
        """
        return self.username