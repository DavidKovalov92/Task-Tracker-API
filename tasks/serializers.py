from rest_framework import serializers
from .models import Team, Task

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'title', 'description', 'members', 'creator']
        read_only_fields = ['id']


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
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']