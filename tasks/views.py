from enum import member
from celery import Task
from rest_framework.viewsets import ModelViewSet
from users.permissions import IsAdminOrManager, RoleHelper
from .serializers import TeamSerializer, TaskSerializer, TaskChangeLogSerializer
from .models import TaskChangeLog, Team, Task
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
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
        task = serializer.save(creator=self.request.user)

        TaskChangeLog(
            task=task,
            user=self.request.user,
            field_changed='created',
            old_value='',
            new_value=f'Task created with title "{task.title}"'
        )

    def perform_update(self, serializer):
        task = self.get_object()

        old_task_data = {
            'title': task.title, 
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'assignee': str(task.assignee) if task.assignee else None,
            'team': str(task.team) if task.team else None,
        }

        updated_task = serializer.save()

        for field, old_value in old_task_data.items():
            new_value = getattr(updated_task, field)
            if str(old_value) != str(new_value):
                TaskChangeLog.objects.create(
                    task=updated_task,
                    user=self.request.user,
                    field_changed=field,
                    old_value=str(old_value),
                    new_value=str(new_value)
                )

    def perform_destroy(self, instance):
        TaskChangeLog.objects.create(
                    task=instance,
                    user=self.request.user,
                    field_changed='deleted',
                    old_value=f'Task "{instance.title}" is deleted',
                    new_value=''
                )
        instance.delete()


    
    @action(detail=True, methods=['POST'], url_path='assign')
    def assign_task(self, request, pk=None):
        task = self.get_object()
        assignee_id = request.data.get('assignee')

        if not assignee_id:
            return Response({'detail': 'assignee_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignee = User.objects.get(pk=assignee_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        old_assignee = task.assignee
        task.assignee = assignee
        task.save()

        TaskChangeLog(
            task=task,
            user=request.user,
            field_changed='assignee',
            old_value=str(old_assignee) if old_assignee else '',
            new_value=str(assignee)
        )



        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], url_path='change-status')
    def change_status(self, request, pk=None):
        task = self.get_object()
        status = request.data.get('status')

        if not status:
            return Response({'status': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = task.status
        task.status = status
        task.save()

        TaskChangeLog(
            task=task,
            user=request.user,
            field_changed='status',
            old_value=old_status,
            new_value=status,
        )

        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'], url_path='history')
    def history(self, request, pk=None):
        task = self.get_object()
        change_logs = task.change_logs.all().order_by('-created_at')
        serializer = TaskChangeLogSerializer(change_logs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
