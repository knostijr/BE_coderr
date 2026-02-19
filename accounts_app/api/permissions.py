"""Custom permissions for accounts app."""

# Third-party imports
from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """Allow only the profile owner to edit their profile.

    Read access is granted to all authenticated users.
    Write access is restricted to the profile owner only.
    """

    def has_object_permission(self, request, view, obj):
        """Check if requesting user owns this profile.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The User object being accessed.

        Returns:
            bool: True if read-only or user is the owner.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user