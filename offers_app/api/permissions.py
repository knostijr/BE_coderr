"""Custom permissions for offers app."""

# Third-party imports
from rest_framework import permissions


class IsBusinessUser(permissions.BasePermission):
    """Allow only business users to create offers."""

    def has_permission(self, request, view):
        """Check if user is business type for write operations.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if safe method or user is business type.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.type == 'business'


class IsOfferOwner(permissions.BasePermission):
    """Allow only the offer creator to edit or delete."""

    def has_object_permission(self, request, view, obj):
        """Check if requesting user owns this offer.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Offer object.

        Returns:
            bool: True if safe method or user is the creator.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user