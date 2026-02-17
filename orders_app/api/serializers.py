"""Serializers for orders_app."""

# Third-party
from rest_framework import serializers

# Local
from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for reading orders.

    Includes fields from related OfferDetail per API spec:
    title, revisions, delivery_time_in_days, price, features, offer_type.
    """

    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(
        source='offer_detail.delivery_time_in_days', read_only=True
    )
    price = serializers.DecimalField(
        source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True
    )
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user',
            'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'customer_user', 'business_user',
            'created_at', 'updated_at',
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new order.

    Accepts offer_detail_id and auto-fills customer/business users.
    """

    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['offer_detail_id']

    def validate_offer_detail_id(self, value):
        """Validate that OfferDetail exists.

        Args:
            value (int): OfferDetail ID.

        Returns:
            int: Validated ID.

        Raises:
            ValidationError: If not found.
        """
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError("OfferDetail not found.")
        return value

    def create(self, validated_data):
        """Create order with users auto-filled from offer.

        Args:
            validated_data (dict): Validated data.

        Returns:
            Order: Created order.
        """
        offer_detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])
        return Order.objects.create(
            customer_user=self.context['request'].user,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail
        )


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status only.

    Used by business users to update status.
    """

    class Meta:
        model = Order
        fields = ['status']