"""API views for offers app."""

# Third-party imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

# Local imports
from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for offer CRUD.

    list:     GET /api/offers/ - public, paginated, filterable
    create:   POST /api/offers/ - business users only, returns full details
    retrieve: GET /api/offers/{id}/ - auth required, url-only details
    update:   PATCH /api/offers/{id}/ - owner only, returns full details
    destroy:  DELETE /api/offers/{id}/ - owner only
    """

    queryset = Offer.objects.all().prefetch_related('details', 'user')
    pagination_class = PageNumberPagination 
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_permissions(self):
        """Return permissions based on action.

        Returns:
            list: Permission instances for the current action.
        """
        if self.action == 'list':
            return []
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsBusinessUser(), IsOfferOwner()]

    def get_serializer_class(self):
        """Return serializer based on action.

        Returns:
            Serializer class for the current action.
        """
        if self.action == 'list':
            return OfferListSerializer
        if self.action == 'retrieve':
            return OfferRetrieveSerializer
        return OfferCreateUpdateSerializer

    def perform_create(self, serializer):
        """Save offer with current user as creator.

        Args:
            serializer: Validated serializer instance.
        """
        serializer.save(user=self.request.user)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for GET /api/offerdetails/{id}/ - auth required."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]