"""Admin configuration for offers_app."""

# Third-party
from django.contrib import admin

# Local
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Inline editor for offer packages."""

    model = OfferDetail
    extra = 1
    fields = ['title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions', 'features']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin for Offer model with inline packages."""

    list_display = ['title', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin for OfferDetail model."""

    list_display = ['offer', 'offer_type', 'price', 'delivery_time_in_days']
    list_filter = ['offer_type']