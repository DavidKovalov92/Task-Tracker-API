from django.db import models
from project.settings import AUTH_USER_MODEL

# Create your models here.
class Status(models.TextChoices):
    TODO = 'todo', 'ToDo'
    IN_PROGRESS = 'in_progress', 'In Progress'
    REVIEW = 'review', 'Review'
    DONE = 'done', 'Done'
    CANCELED = 'canceled', 'Canceled'

class Priority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.LOWб
        blank=True,
        null=True
    )
    deadline = models.DateTimeField(null=True, blank=True)
    assignee = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned',
    )

    creator = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks_created',
    )


    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title