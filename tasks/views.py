from rest_framework.viewsets import ModelViewSet
from users.permissions import IsAdminOrManager, RoleHelper
from .serializers import TeamSerializer
from .models import Team
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

class TeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if RoleHelper.is_admin(user):
            return Team.objects.all()
        elif RoleHelper.is_manager(user):
            return Team.objects.filter(creator=user)
        else:
            return Team.objects.filter(members=user)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return super().get_permissions()
    
    def check_object_permissions(self, request, obj):
        user = request.user
        if not (
            RoleHelper.is_admin(user) or
            (RoleHelper.is_manager(user) and obj.creator == user) or
            (user in obj.members.all())
        ):
            raise PermissionDenied("You do not have access to this team.")
        return True

    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


