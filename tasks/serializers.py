from rest_framework import serializers
from .models import Team, Task, TaskChangeLog


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'deadline',
            'assignee',
            'creator',
            'is_active',
            'created_at',
            'updated_at',
            'team',
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']


class TeamSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'title', 'description', 'members', 'creator', 'tasks']
        read_only_fields = ['id']


class TaskChangeLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = TaskChangeLog
        fields = [
            'task',
            'user',
            'field_changed',
            'old_value',
            'new_value',
            'created_at',
        ]