"""Models for order management."""

# Third-party
from django.conf import settings
from django.db import models

# Local
from offers_app.models import OfferDetail


class Order(models.Model):
    """A customer order for an offer package.

    Attributes:
        customer_user (ForeignKey): Customer who placed the order.
        business_user (ForeignKey): Business user fulfilling the order.
        offer_detail (ForeignKey): The specific package ordered.
        status (str): 'in_progress', 'completed', or 'cancelled'.
        created_at (datetime): Auto-set on creation.
        updated_at (datetime): Auto-set on update.
    """

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
        OfferDetail,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        """Return order ID and status."""
        return f"Order #{self.id} - {self.status}"