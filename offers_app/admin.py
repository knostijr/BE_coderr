"""Admin configuration for offers app."""

# Third-party imports
from django.contrib import admin

# Local imports
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Inline admin for offer packages."""

    model = OfferDetail
    extra = 1
    fields = ['title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions', 'features']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin interface for Offer model."""

    list_display = ['title', 'user', 'created_at']
    search_fields = ['title', 'description']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin interface for OfferDetail model."""

    list_display = ['offer', 'offer_type', 'price', 'delivery_time_in_days']
    list_filter = ['offer_type']