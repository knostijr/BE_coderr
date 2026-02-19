"""Models for the offers app."""

# Third-party imports
from django.conf import settings
from django.db import models


class Offer(models.Model):
    """A freelancer service offer with multiple packages."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        ordering = ['-created_at']

    def __str__(self):
        """Return offer title.

        Returns:
            str: The offer title.
        """
        return self.title


class OfferDetail(models.Model):
    """A specific package tier for an offer (basic/standard/premium)."""

    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='details'
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Offer Detail'
        verbose_name_plural = 'Offer Details'
        unique_together = ('offer', 'offer_type')

    def __str__(self):
        """Return offer title with package type.

        Returns:
            str: Offer title and package type.
        """
        return f"{self.offer.title} - {self.offer_type}"