from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins of an object to edit it.
    """

    def has_permission(self, request, view):
        """
        Allows read-only access to unauthenticated users,
        and full access to admin users.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the staff.
        return request.user.is_authenticated and request.user.is_staff