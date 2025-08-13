from django.db import models
from users.models import CustomUser
from django.contrib.postgres.fields import ArrayField

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

class NotificationType(models.TextChoices):
    ASSIGN = 'assign', 'Assign'
    UPDATED = 'updated', 'Updated'

class NotificationStatus(models.TextChoices):
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'


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
        default=Priority.LOW,
        blank=True,
        null=True
    )
    deadline = models.DateTimeField(null=True, blank=True)
    assignee = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned',
    )

    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tasks_created',
    )


    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
    )
    reminders_sent = ArrayField(models.DurationField(), default=list, blank=True)


    def reminder_sent(self, delta):
        return delta in self.reminders_sent

    def mark_reminder_sent(self, delta):
        self.reminders_sent.append(delta)
        self.save(update_fields=['reminders_sent'])

    def __str__(self):
        return self.title
    
class Team(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(CustomUser, related_name='teams', blank=True)
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='teams_created'
    )

    def __str__(self):
        return self.title

class TaskChangeLog(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='change_logs')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title}: {self.field_changed} changed by {self.user} at {self.created_at}"

class NotificationLog(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='notification_logs')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.type} for {self.user} on {self.task.title} - {self.status}"
