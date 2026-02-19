"""Custom permissions for orders app."""

# Third-party imports
from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    """Allow only customer type users to create orders."""

    def has_permission(self, request, view):
        """Check if user is a customer.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if user is authenticated and customer type.
        """
        return request.user.is_authenticated and request.user.type == 'customer'


class IsBusinessUserOfOrder(permissions.BasePermission):
    """Allow only the business user of an order to update its status."""

    def has_object_permission(self, request, view, obj):
        """Check if user is the business user for this order.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Order object.

        Returns:
            bool: True if user is business type and assigned to order.
        """
        if request.user.type != 'business':
            return False
        return obj.business_user == request.user


class IsAdminUser(permissions.BasePermission):
    """Allow only admin/staff users to delete orders."""

    def has_permission(self, request, view):
        """Check if user is admin/staff.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if user is staff or superuser.
        """
        return request.user.is_authenticated and request.user.is_staff