from django_filters import rest_framework as filters
from .models import Task, Team

class TaskFilter(filters.FilterSet):
    deadline_lte = filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')
    deadline_gte = filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')

    class Meta:
        model = Task
        fields = [
            'status',
            'priority',
            'creator',
            'assignee',
            'team',
            'deadline_lte',
            'deadline_gte',
        ]

class TeamFilter(filters.FilterSet):
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    creator_id = filters.NumberFilter(field_name='creator__id')
    member_id = filters.NumberFilter(field_name='members__id')

    class Meta:
        model = Team
        fields = [
            'is_active',
            'creator_id',
            'member_id',
            'created_before',
            'created_after',
        ]
