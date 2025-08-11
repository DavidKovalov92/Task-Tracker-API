from rest_framework.permissions import BasePermission
from .models import Role

class RoleHelper:
    @staticmethod
    def is_admin(user):
        return user.role == Role.ADMIN
    
    @staticmethod
    def is_manager(user):
        return user.role == Role.MANAGER
    
    @staticmethod
    def is_user(user):
        return user.role == Role.USER

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and RoleHelper.is_admin(request.user)

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and RoleHelper.is_manager(request.user)

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and RoleHelper.is_user(request.user)
    
class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.ADMIN, Role.MANAGER]
