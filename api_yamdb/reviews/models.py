from django.db import models
from django.contrib.auth.models import AbstractUser

ROLES = [
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
]


class CustomUser(AbstractUser):
    """Кастомизация модели пользователя."""
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user', max_length=9)


class Category(models.Model):
    """Модель для категорий."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
