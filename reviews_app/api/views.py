"""API views for reviews app and base-info endpoint."""

# Third-party imports
from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from offers_app.models import Offer
from reviews_app.models import Review

from .permissions import IsCustomerUser, IsReviewOwner
from .serializers import ReviewSerializer

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for review CRUD with filtering.

    list:     GET /api/reviews/ - direct array, filterable
    create:   POST /api/reviews/ - customer only, one per business
    update:   PATCH /api/reviews/{id}/ - reviewer only
    destroy:  DELETE /api/reviews/{id}/ - reviewer only
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return reviews filtered by business_user_id or reviewer_id.

        Returns:
            QuerySet: Filtered reviews.
        """
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset

    def get_permissions(self):
        """Return permissions based on action.

        Returns:
            list: Permission instances for the current action.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated(), IsReviewOwner()]

    def list(self, request, *args, **kwargs):
        """Return reviews as direct array without pagination.

        Args:
            request: HTTP request.

        Returns:
            Response: Direct array of reviews.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create review and return 201.

        Args:
            request: HTTP request.

        Returns:
            Response: Created review with 201 status.
        """
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BaseInfoView(APIView):
    """Public endpoint returning platform statistics.

    GET /api/base-info/ - no authentication required.
    average_rating rounded to 1 decimal place per endpoint docs.
    """

    permission_classes = []

    def get(self, request):
        """Return aggregate platform statistics.

        Args:
            request: HTTP request.

        Returns:
            Response: Statistics with 200 status.
        """
        avg_data = Review.objects.aggregate(Avg('rating'))
        avg_rating = avg_data['rating__avg']
        if avg_rating is not None:
            avg_rating = round(avg_rating, 1)

        return Response({
            'review_count': Review.objects.count(),
            'average_rating': avg_rating,
            'business_profile_count': User.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count(),
        })