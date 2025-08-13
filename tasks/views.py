from celery import Task
from rest_framework.viewsets import ModelViewSet
from .email import generate_task_email
from users.permissions import IsAdminOrManager, RoleHelper
from .serializers import TeamSerializer, TaskSerializer, TaskChangeLogSerializer
from .models import Team, Task
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from .helpers import task_change_log, log_notification
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import TaskFilter, TeamFilter
from .tasks import invalidate_task_cache, send_email_task, export_tasks_s3
from .cache import make_cache_key, cache_get, cache_set
from celery.result import AsyncResult


User = get_user_model()


class TeamViewSet(ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TeamFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    


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

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'deadline', 'priority']


    def list(self, request, *args, **kwargs):
        user = request.user
        base_key = "tasks:list"
        query_params = request.query_params.dict()
        cache_key = make_cache_key(user.id, base_key, query_params)
        cached_data = cache_get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache_set(cache_key, response.data, ttl=120)
        return response


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
        
        assignee_id = self.request.data.get("assignee")
        assignee = None
        if assignee_id:
            try:
                assignee = User.objects.get(pk=assignee_id)
            except User.DoesNotExist:
                assignee = None

        invalidate_task_cache.delay(user_id=self.request.user.id)

        task_change_log(task, self.request.user, 'created', '', f'Task created with title "{task.title}"')

        if assignee and assignee.email:
            html_body = generate_task_email(task, self.request.user)
            send_email_task.delay(assignee.email, html_body)

        log_notification(task, assignee)

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

        invalidate_task_cache.delay(task_id=task.id, user_id=self.request.user.id)

        for field, old_value in old_task_data.items():
            new_value = getattr(updated_task, field)
            if str(old_value) != str(new_value):
                task_change_log(updated_task, self.request.user, field, str(old_value), str(new_value))

    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs.get('id')
        cache_key = f"tasks:detail:{task_id}"

        cached_data = cache_get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().retrieve(request, *args, **kwargs)
        cache_set(cache_key, response.data, ttl=300)
        return response
    

    def perform_destroy(self, instance):
        task_id = instance.id

        task_change_log(instance, self.request.user, 'deleted', f'Task "{instance.title}" is deleted', '')
        instance.delete()
        invalidate_task_cache.delay(task_id=task_id, user_id=self.request.user.id)


    
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

        task_change_log(task, request.user, 'assignee', str(old_assignee) if old_assignee else '', str(assignee))

        if assignee.email:
            html_body = generate_task_email(task, request.user)
            send_email_task.delay(assignee.email, html_body)


        log_notification(task, assignee)


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

        task_change_log(task, request.user, 'status', old_status, status)

        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'], url_path='history')
    def history(self, request, pk=None):
        task = self.get_object()
        change_logs = task.change_logs.all().order_by('-created_at')
        serializer = TaskChangeLogSerializer(change_logs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path='export')
    def export(self, request):
        export_format = request.query_params.get('format', 'csv').lower()
        filters = {}

        if 'status' in request.query_params:
            filters['status'] = request.query_params.get('status')
        if 'deadline__gte' in request.query_params:
            filters['deadline__gte'] = request.query_params.get('deadline__gte')
        if 'deadline__lte' in request.query_params:
            filters['deadline__lte'] = request.query_params.get('deadline__lte')

        task = export_tasks_s3.delay(request.user.id, export_format, filters)

        return Response({
            'task_id': task.id,
            'status': 'started',
            'message': 'Export started. Use /export-status?task_id=... to get download link.'
        })


    @action(detail=False, methods=['GET'], url_path='export-link')
    def export_status(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({"error": "task_id required"}, status=400)

        res = AsyncResult(task_id)

        if res.ready():
            url = res.get()
            url = url.replace("minio:9000", "127.0.0.1:9000")
            return Response({"status": "done", "url": url})
        else:
            return Response({"status": "pending"})