"""Custom permissions for reviews app."""

# Third-party imports
from rest_framework import permissions


class IsCustomerUser(permissions.BasePermission):
    """Allow only customer type users to create reviews."""

    def has_permission(self, request, view):
        """Check if user is a customer.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if user is authenticated and customer type.
        """
        return request.user.is_authenticated and request.user.type == 'customer'


class IsReviewOwner(permissions.BasePermission):
    """Allow only the review author to edit or delete."""

    def has_object_permission(self, request, view, obj):
        """Check if requesting user is the reviewer.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Review object.

        Returns:
            bool: True if user is the reviewer.
        """
        return obj.reviewer == request.user