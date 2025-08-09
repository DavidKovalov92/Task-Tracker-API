from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        DEVELOPER = 'developer', 'Developer'

    role = models.TextChoices(
        max_length=20,
        choices=Role.choices,
        default=Role.DEVELOPER,
    )
