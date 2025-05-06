from rest_framework.permissions import BasePermission
from .models import Users

class IsAdminUserProfile(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        try:
            return user.users.role == 'admin'
        except Users.DoesNotExist:
            return False