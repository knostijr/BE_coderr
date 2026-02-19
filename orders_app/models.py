"""Models for orders app."""

# Third-party imports
from django.conf import settings
from django.db import models

# Local imports
from offers_app.models import OfferDetail


class Order(models.Model):
    """Customer order for a specific offer package."""

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_as_customer'
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_as_business'
    )
    offer_detail = models.ForeignKey(
        OfferDetail, on_delete=models.CASCADE, related_name='orders'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        """Return order ID and status.

        Returns:
            str: Order identifier with status.
        """
        return f"Order #{self.id} - {self.status}"