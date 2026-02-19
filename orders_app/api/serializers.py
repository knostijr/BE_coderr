"""Serializers for orders app."""

# Third-party imports
from rest_framework import serializers

# Local imports
from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for reading orders including OfferDetail fields."""

    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(
        source='offer_detail.revisions', read_only=True
    )
    delivery_time_in_days = serializers.IntegerField(
        source='offer_detail.delivery_time_in_days', read_only=True
    )
    price = serializers.DecimalField(
        source='offer_detail.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user',
            'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_user', 'business_user', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new order from offer_detail_id."""

    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['offer_detail_id']

    def validate_offer_detail_id(self, value):
        """Validate that the OfferDetail exists.

        Args:
            value (int): The offer detail ID.

        Returns:
            int: Validated ID.

        Raises:
            serializers.ValidationError: If OfferDetail not found.
        """
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError("OfferDetail not found.")
        return value

    def create(self, validated_data):
        """Create order with auto-filled users from offer detail.

        Args:
            validated_data (dict): Validated data.

        Returns:
            Order: Created order instance.
        """
        offer_detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])
        return Order.objects.create(
            customer_user=self.context['request'].user,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail
        )


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status only."""

    class Meta:
        model = Order
        fields = ['status']