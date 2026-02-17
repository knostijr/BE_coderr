"""Serializers for accounts_app."""

# Third-party
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration.

    Validates that password and repeated_password match.
    Creates user with hashed password.

    Fields:
        username (str): Unique username.
        email (str): Email address (required).
        password (str): Password (write-only).
        repeated_password (str): Confirmation (write-only).
        type (str): 'customer' or 'business' (optional).
    """

    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    repeated_password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'email': {'required': True},
            'type': {'required': False}
        }

    def validate(self, attrs):
        """Validate that both password fields match.

        Args:
            attrs (dict): Field values.

        Returns:
            dict: Validated attributes.

        Raises:
            ValidationError: If passwords don't match.
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """Create user with hashed password and type.

        Args:
            validated_data (dict): Validated data.

        Returns:
            User: New user instance.
        """
        validated_data.pop('repeated_password')
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data.get('type', 'customer')
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for login credentials.

    Fields:
        username (str): Username.
        password (str): Password (write-only).
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data.

    Uses 'user' as ID field name per API spec.
    All string fields return empty string instead of null.

    Fields:
        user (int): User ID (source=id, read-only).
        username, first_name, last_name, file, location,
        tel, description, working_hours, type, email,
        created_at (read-only).
    """

    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name',
            'file', 'location', 'tel', 'description',
            'working_hours', 'type', 'email', 'created_at',
        ]
        read_only_fields = ['user', 'created_at']