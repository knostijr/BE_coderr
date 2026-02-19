"""Custom filters for offers app."""

# Third-party imports
import django_filters

# Local imports
from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Filter for Offer queryset per endpoint documentation."""

    creator_id = django_filters.NumberFilter(field_name='user__id')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_delivery_time = django_filters.NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_min_price(self, queryset, name, value):
        """Filter offers with at least one package >= min price.

        Args:
            queryset: Current offer queryset.
            name (str): Field name.
            value: Minimum price value.

        Returns:
            QuerySet: Filtered offers.
        """
        return queryset.filter(details__price__gte=value).distinct()

    def filter_max_delivery_time(self, queryset, name, value):
        """Filter offers with at least one package <= max delivery days.

        Args:
            queryset: Current offer queryset.
            name (str): Field name.
            value: Maximum delivery days.

        Returns:
            QuerySet: Filtered offers.
        """
        return queryset.filter(
            details__delivery_time_in_days__lte=value
        ).distinct()