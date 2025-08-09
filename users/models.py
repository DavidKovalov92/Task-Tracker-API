from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    MANAGER = 'manager', 'Manager'
    USER = 'developer', 'Developer'

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

class Team(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)
    members = models.ManyToManyField('CustomUser', related_name='teams', blank=True)

    def __str__(self):
        return self.title