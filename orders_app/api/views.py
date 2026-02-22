"""API views for orders app."""

# Third-party imports
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from orders_app.models import Order

from .permissions import IsAdminUser, IsBusinessUserOfOrder, IsCustomerUser
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer

User = get_user_model()


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for order management.

    list:           GET /api/orders/ - direct array, user's own orders
    create:         POST /api/orders/ - customer only
    partial_update: PATCH /api/orders/{id}/ - business user only
    destroy:        DELETE /api/orders/{id}/ - admin only
    """

    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Return all orders for update/delete, own orders for list.

        Returning all orders for update/delete ensures permissions
        return 403 instead of 404 for unauthorized users.

        Returns:
            QuerySet: Filtered or full order queryset.
        """
        user = self.request.user
        base = Order.objects.select_related(
            'offer_detail', 'customer_user', 'business_user'
        )
        if self.action in ['partial_update', 'update', 'destroy']:
            return base.all()
        return base.filter(Q(customer_user=user) | Q(business_user=user))

    def get_serializer_class(self):
        """Return serializer based on action.

        Returns:
            Serializer class for the current action.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action in ['partial_update', 'update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        """Return permissions based on action.

        Returns:
            list: Permission instances for the current action.
        """
        if self.action == 'create':
            return [IsCustomerUser()]
        if self.action in ['partial_update', 'update']:
            return [IsAuthenticated(), IsBusinessUserOfOrder()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """Return orders as direct array without pagination.

        Args:
            request: HTTP request.

        Returns:
            Response: Direct array of orders.
        """
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create order and return full order data.

        Args:
            request: HTTP request with offer_detail_id.

        Returns:
            Response: Full order data with 201 status.
        """
        create_serializer = OrderCreateSerializer(
            data=request.data, context={'request': request}
        )
        create_serializer.is_valid(raise_exception=True)
        order = create_serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """Update order status and return full order data.

        Args:
            request: HTTP request with status field.

        Returns:
            Response: Full order data with 200 status.
        """
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full order data using OrderSerializer (all fields)
        return Response(OrderSerializer(instance).data)


class OrderCountView(APIView):
    """Return in-progress order count for a business user.

    GET /api/order-count/{business_user_id}/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return count of in-progress orders for business user.

        Args:
            request: HTTP request.
            business_user_id (int): ID of the business user.

        Returns:
            Response: Order count or 404.
        """
        business_user = get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user=business_user, status='in_progress'
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """Return completed order count for a business user.

    GET /api/completed-order-count/{business_user_id}/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return count of completed orders for business user.

        Args:
            request: HTTP request.
            business_user_id (int): ID of the business user.

        Returns:
            Response: Completed order count or 404.
        """
        business_user = get_object_or_404(User, id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user=business_user, status='completed'
        ).count()
        return Response({'completed_order_count': count})