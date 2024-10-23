from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = [
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
]

CHARFIELD_MAX_LENGTH = 150
NAME_MAX_LENGTH = 256


class CustomUser(AbstractUser):
    """Кастомизация модели пользователя."""
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user',
                            max_length=CHARFIELD_MAX_LENGTH)


class Category(models.Model):
    """Модель для категорий."""
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
