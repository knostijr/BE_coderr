"""Custom permissions for offers_app."""

# Third-party
from rest_framework import permissions


class IsBusinessUser(permissions.BasePermission):
    """Allow only users with type='business' to create offers."""

    def has_permission(self, request, view):
        """Check if user is a business user.

        Args:
            request: HTTP request.
            view: View being accessed.

        Returns:
            bool: True if business user.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.type == 'business'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow only the offer owner to edit or delete."""

    def has_object_permission(self, request, view, obj):
        """Check if user owns this offer.

        Args:
            request: HTTP request.
            view: View being accessed.
            obj: Offer object.

        Returns:
            bool: True if permitted.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user