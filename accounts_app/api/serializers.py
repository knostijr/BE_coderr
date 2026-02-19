"""Serializers for authentication and user profiles."""

# Third-party imports
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration.

    Validates matching passwords and creates user with hashed password.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    repeated_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'email': {'required': True},
            'type': {'required': False},
        }

    def validate(self, attrs):
        """Validate that both password fields match.

        Args:
            attrs (dict): Input field values.

        Returns:
            dict: Validated attributes.

        Raises:
            serializers.ValidationError: If passwords do not match.
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """Create new user with hashed password.

        Args:
            validated_data (dict): Validated data from serializer.

        Returns:
            User: Newly created user instance.
        """
        validated_data.pop('repeated_password')
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data.get('type', 'customer')
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for user login credentials."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profiles.

    Uses 'user' as ID field per endpoint documentation.
    String fields never return null, defaults to empty string.
    Does NOT include updated_at per endpoint documentation.
    """

    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        read_only_fields = ['user', 'username', 'created_at']