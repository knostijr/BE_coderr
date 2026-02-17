"""Custom permissions for accounts_app."""

# Third-party
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow only the profile owner to edit their profile.

    Safe methods (GET, HEAD, OPTIONS) are allowed for all
    authenticated users. Write methods only for the owner.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns this object.

        Args:
            request: HTTP request.
            view: View being accessed.
            obj: User object.

        Returns:
            bool: True if permitted.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user