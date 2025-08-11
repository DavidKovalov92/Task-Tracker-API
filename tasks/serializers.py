from rest_framework import serializers
from .models import Team, Task


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
