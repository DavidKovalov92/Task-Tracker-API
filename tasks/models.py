from django.db import models

# Create your models here.
class Status(models.TextChoices):
    TODO = 'todo', 'ToDo'
    IN_PROGRESS = 'in_progress', 'In Progress'
    REVIEW = 'review', 'Review'
    DONE = 'done', 'Done'
    CANCELED = 'canceled', 'Canceled'

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
