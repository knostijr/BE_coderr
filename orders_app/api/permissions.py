"""Custom permissions for orders_app."""

# Third-party
from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    """Allow only users with type='customer' to create orders."""

    def has_permission(self, request, view):
        """Check if user is a customer.

        Args:
            request: HTTP request.
            view: View being accessed.

        Returns:
            bool: True if customer user.
        """
        return request.user.is_authenticated and request.user.type == 'customer'


class IsBusinessUserOfOrder(permissions.BasePermission):
    """Allow only the business user of an order to update its status."""

    def has_object_permission(self, request, view, obj):
        """Check if user is the business user of this order.

        Args:
            request: HTTP request.
            view: View being accessed.
            obj: Order object.

        Returns:
            bool: True if permitted.
        """
        return (
            request.user.type == 'business'
            and obj.business_user == request.user
        )


class IsAdminUser(permissions.BasePermission):
    """Allow only admin/staff users to delete orders."""

    def has_permission(self, request, view):
        """Check if user is staff/admin.

        Args:
            request: HTTP request.
            view: View being accessed.

        Returns:
            bool: True if staff user.
        """
        return request.user.is_authenticated and request.user.is_staff