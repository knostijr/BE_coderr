"""Serializers for offers app."""

# Third-party imports
from django.contrib.auth import get_user_model
from rest_framework import serializers

# Local imports
from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full OfferDetail serializer - used for create/update responses."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type'
        ]
        read_only_fields = ['id']


class OfferDetailURLSerializer(serializers.ModelSerializer):
    """OfferDetail serializer returning only id and url - used for list/retrieve."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Build URL for this offer detail.

        Args:
            obj: OfferDetail instance.

        Returns:
            str: URL path to detail endpoint.
        """
        return f"/api/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    """Nested user info for user_details field in offer list."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/offers/ - includes user_details and url-only details."""

    user = serializers.IntegerField(source='user.id', read_only=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)
    details = OfferDetailURLSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_min_price(self, obj):
        """Return minimum price across all packages.

        Args:
            obj: Offer instance.

        Returns:
            float or None: Minimum price.
        """
        prices = obj.details.values_list('price', flat=True)
        return float(min(prices)) if prices else None

    def get_min_delivery_time(self, obj):
        """Return minimum delivery time across all packages.

        Args:
            obj: Offer instance.

        Returns:
            int or None: Minimum delivery days.
        """
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/offers/{id}/ - url-only details, no user_details."""

    user = serializers.IntegerField(source='user.id', read_only=True)
    details = OfferDetailURLSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time'
        ]

    def get_min_price(self, obj):
        """Return minimum price across all packages."""
        prices = obj.details.values_list('price', flat=True)
        return float(min(prices)) if prices else None

    def get_min_delivery_time(self, obj):
        """Return minimum delivery time across all packages."""
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for POST/PATCH - nested full details in request AND response."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """Validate that exactly 3 details are provided on create.

        Args:
            value (list): List of detail data.

        Returns:
            list: Validated detail data.

        Raises:
            serializers.ValidationError: If not exactly 3 on create.
        """
        if self.instance is None and len(value) != 3:
            raise serializers.ValidationError(
                "An offer must have exactly 3 details (basic, standard, premium)."
            )
        return value

    def create(self, validated_data):
        """Create offer with all nested details.

        Args:
            validated_data (dict): Validated serializer data.

        Returns:
            Offer: Created offer instance.
        """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Update offer and optionally update details by offer_type.

        Args:
            instance: Existing Offer instance.
            validated_data (dict): Validated serializer data.

        Returns:
            Offer: Updated offer instance.
        """
        details_data = validated_data.pop('details', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()

        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')
            OfferDetail.objects.filter(
                offer=instance, offer_type=offer_type
            ).update(**{k: v for k, v in detail_data.items() if k != 'offer_type'})

        return instance