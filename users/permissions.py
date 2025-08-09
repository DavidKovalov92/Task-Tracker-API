from rest_framework.permissions import BasePermission
from .models import User

class RoleHelper:
    @staticmethod
    def is_admin(user):
        return user.role == UserRole.ADMIN

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and RoleHelper.is_admin(request.user)
