from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Custom permission to only allow users with admin role or staff status.
    """
    def has_permission(self, request, view):
        # Allow access if user is staff or has the 'admin' role
        return request.user and (request.user.is_staff or request.user.role == 'admin')
