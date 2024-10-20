from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = [
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
]


class CustomUser(AbstractUser):
    """Кастомизация модели пользователя."""
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user', max_length=9)
