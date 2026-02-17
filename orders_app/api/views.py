"""API views for orders_app."""

# Standard library
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Third-party
from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local
from orders_app.models import Order

from .permissions import IsAdminUser, IsBusinessUserOfOrder, IsCustomerUser
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer

User = get_user_model()


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet for order operations.

    list:   GET /api/orders/ - own orders (auth required)
    create: POST /api/orders/ - customers only
    update: PATCH /api/orders/{id}/ - business user only
    destroy: DELETE /api/orders/{id}/ - admin only
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return orders where user is customer or business.

        Returns:
            QuerySet: Filtered orders for current user.
        """
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).select_related('offer_detail', 'customer_user', 'business_user')

    def get_serializer_class(self):
        """Return serializer based on action.

        Returns:
            Serializer class.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action in ['update', 'partial_update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        """Return permissions based on action.

        Returns:
            list: Permission instances.
        """
        if self.action == 'create':
            return [IsAuthenticated(), IsCustomerUser()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsBusinessUserOfOrder()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """Return plain array of orders (no pagination).

        Args:
            request: HTTP request.

        Returns:
            Response: Array of orders.
        """
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create order and return full order data.

        Args:
            request: HTTP request.

        Returns:
            Response: Created order (201) or error.
        """
        serializer = OrderCreateSerializer(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderCountView(APIView):
    """Handle GET /api/order-count/{business_user_id}/ - auth required."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return count of in-progress orders for a business user.

        Args:
            request: HTTP request.
            business_user_id (int): Business user ID.

        Returns:
            Response: order_count (200) or 404.
        """
        get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status='in_progress'
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """Handle GET /api/completed-order-count/{business_user_id}/ - auth required."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return count of completed orders for a business user.

        Args:
            request: HTTP request.
            business_user_id (int): Business user ID.

        Returns:
            Response: completed_order_count (200) or 404.
        """
        get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status='completed'
        ).count()
        return Response({'completed_order_count': count})