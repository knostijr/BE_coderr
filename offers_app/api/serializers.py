"""Serializers for offers_app.

Different serializers per use case:
- List view: user (int), user_details, details with id+url, computed fields
- Detail view: same structure as list
- Create: accepts nested details (must have all 3 types)
- Update: can update individual details by offer_type
"""

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import serializers

# Local
from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full serializer for OfferDetail (for create/update and offerdetails endpoint).

    Fields: id, title, revisions, delivery_time_in_days, price, features, offer_type.
    """

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type'
        ]
        read_only_fields = ['id']


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serializer that returns id and url for offer details.

    Used in list and retrieve views per API spec.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Build URL path for this offer detail.

        Args:
            obj: OfferDetail instance.

        Returns:
            str: URL path.
        """
        return f"/api/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    """Nested user info for user_details field in offer responses.

    Fields: first_name, last_name, username.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for offer list and detail views.

    Per API spec:
    - 'user' is the user ID (int)
    - 'user_details' is nested {first_name, last_name, username}
    - 'details' contains objects with id and url
    - 'min_price' and 'min_delivery_time' are computed
    """

    user_details = UserDetailsSerializer(source='user', read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

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
            int or None: Minimum delivery time.
        """
        times = obj.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new offer with 3 packages.

    Requires exactly 3 details: basic, standard, premium.
    Returns full details on success.
    """

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """Validate that exactly 3 details with correct types are provided.

        Args:
            value (list): List of detail data.

        Returns:
            list: Validated details.

        Raises:
            ValidationError: If not exactly 3 unique types provided.
        """
        types = [d['offer_type'] for d in value]
        required = {'basic', 'standard', 'premium'}

        if set(types) != required or len(types) != 3:
            raise serializers.ValidationError(
                "An offer must have exactly 3 details: basic, standard, and premium."
            )
        return value

    def create(self, validated_data):
        """Create offer with nested details.

        Args:
            validated_data (dict): Validated data.

        Returns:
            Offer: Created offer instance.
        """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer


class OfferUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an offer and its packages.

    Details are identified by offer_type and updated individually.
    Returns full details after update.
    """

    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        """Update offer and optionally update individual packages.

        Args:
            instance: Offer to update.
            validated_data (dict): Validated data.

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