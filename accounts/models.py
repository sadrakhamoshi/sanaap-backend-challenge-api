from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', _('Admin')
    EDITOR = 'EDITOR', _('Editor')
    VIEWER = 'VIEWER', _('Viewer')

class User(AbstractUser):

    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
    )

    def __str__(self):
        return f"{self.username} - {self.role}"
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_editor(self):
        return self.role == UserRole.EDITOR

    @property
    def is_viewer(self):
        return self.role == UserRole.VIEWER