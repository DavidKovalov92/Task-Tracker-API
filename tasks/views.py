from enum import member
from celery import Task
from rest_framework.viewsets import ModelViewSet
from users.permissions import IsAdminOrManager, RoleHelper
from .serializers import TeamSerializer, TaskSerializer
from .models import Team, Task
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
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



class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user 

        if RoleHelper.is_admin(user):
            return Task.objects.all()

        teams_where_creator = Team.objects.filter(creator=user)
        teams_where_member = Team.objects.filter(members=user)
        all_teams = teams_where_creator | teams_where_member

        members_ids = all_teams.values_list('members__id', flat=True)
        if RoleHelper.is_manager(user):
            return Task.objects.filter(
                Q(creator=user) |                  
                Q(assignee=user) |                 
                Q(assignee__id__in=members_ids) 
            ).distinct()

        else:  
            return Task.objects.filter(
                Q(creator=user) |
                Q(assignee=user) |
                Q(assignee__id__in=members_ids)
            ).distinct()
        
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return super().get_permissions()
    
    def check_object_permissions(self, request, obj):
        user = request.user

        if RoleHelper.is_admin(user):
            return True

        if RoleHelper.is_manager(user):
            user_teams = Team.objects.filter(creator=user) | Team.objects.filter(members=user)
            if obj.team and obj.team in user_teams:
                return True

        if obj.team and user in obj.team.members.all():
            return True
    

        raise PermissionDenied("You do not have access to this task.")


    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


