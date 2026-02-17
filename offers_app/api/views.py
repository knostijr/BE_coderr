"""API views for offers_app with filtering, search, and pagination."""

# Third-party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Local
from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .permissions import IsBusinessUser, IsOwnerOrReadOnly
from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferUpdateSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for offer CRUD operations.

    list:   GET /api/offers/ - public, supports filtering
    create: POST /api/offers/ - business users only
    retrieve: GET /api/offers/{id}/ - auth required
    update: PATCH /api/offers/{id}/ - owner only
    destroy: DELETE /api/offers/{id}/ - owner only

    Query parameters: creator_id, min_price, max_delivery_time,
    search, ordering, page_size.
    """

    queryset = Offer.objects.all().prefetch_related('details', 'user')
    permission_classes = [IsAuthenticatedOrReadOnly, IsBusinessUser, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """Return the appropriate serializer for each action.

        Returns:
            Serializer class based on current action.
        """
        if self.action == 'create':
            return OfferCreateSerializer
        if self.action in ['update', 'partial_update']:
            return OfferUpdateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        """Save offer with current user as creator.

        Args:
            serializer: Validated serializer.
        """
        serializer.save(user=self.request.user)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading individual offer packages.

    retrieve: GET /api/offerdetails/{id}/ - auth required
    """

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]