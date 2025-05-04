from rest_framework.permissions import BasePermission
from .models import Users

class IsAdminUserProfile(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.users.role == 'admin'
        except Users.DoesNotExist:
            return False