"""Custom filters for offers_app."""

# Third-party
import django_filters

# Local
from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Filter for Offer queryset based on endpoint documentation.

    Filters:
        creator_id: Filter by user ID.
        min_price: Filter offers with at least one package >= value.
        max_delivery_time: Filter offers with at least one package <= value.
    """

    creator_id = django_filters.NumberFilter(field_name='user__id')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_delivery_time = django_filters.NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_min_price(self, queryset, name, value):
        """Filter offers with at least one package >= min_price.

        Args:
            queryset: Offer queryset.
            name (str): Field name.
            value: Minimum price.

        Returns:
            QuerySet: Filtered offers.
        """
        return queryset.filter(details__price__gte=value).distinct()

    def filter_max_delivery_time(self, queryset, name, value):
        """Filter offers with at least one package <= max_delivery_time.

        Args:
            queryset: Offer queryset.
            name (str): Field name.
            value: Maximum delivery time in days.

        Returns:
            QuerySet: Filtered offers.
        """
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()