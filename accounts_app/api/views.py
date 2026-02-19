"""API views for authentication and user profiles."""

# Third-party imports
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .permissions import IsProfileOwner
from .serializers import LoginSerializer, RegistrationSerializer, UserProfileSerializer

User = get_user_model()


class RegistrationView(APIView):
    """Handle POST /api/registration/ - no auth required."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register new user and return auth token.

        Args:
            request: HTTP request with user data.

        Returns:
            Response: token, username, email, user_id (201) or errors (400).
        """
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Handle POST /api/login/ - no auth required."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and return token.

        Args:
            request: HTTP request with credentials.

        Returns:
            Response: token, username, email, user_id (200) or error (400).
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for profile retrieve and update.

    GET   /api/profile/{pk}/ - retrieve profile (auth required)
    PATCH /api/profile/{pk}/ - update own profile (owner only)
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    http_method_names = ['get', 'patch', 'head', 'options']


class ProfileBusinessListView(APIView):
    """Handle GET /api/profiles/business/ - direct array, no pagination."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return list of all business users.

        Args:
            request: HTTP request.

        Returns:
            Response: Array of business user profiles.
        """
        users = User.objects.filter(type='business')
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)


class ProfileCustomerListView(APIView):
    """Handle GET /api/profiles/customer/ - direct array, no pagination."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return list of all customer users.

        Args:
            request: HTTP request.

        Returns:
            Response: Array of customer user profiles.
        """
        users = User.objects.filter(type='customer')
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)