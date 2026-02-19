"""Serializers for reviews app."""

# Third-party imports
from rest_framework import serializers

# Local imports
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model.

    reviewer is set automatically from request user.
    Validates one review per business user per customer.
    """

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer',
            'rating', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validate that reviewer has not already reviewed this business user.

        Args:
            attrs (dict): Input field values.

        Returns:
            dict: Validated attributes.

        Raises:
            serializers.ValidationError: If review already exists.
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            if Review.objects.filter(
                reviewer=request.user,
                business_user=attrs.get('business_user')
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this business user."
                )
        return attrs