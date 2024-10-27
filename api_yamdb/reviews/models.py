from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .constants import CHARFIELD_MAX_LENGTH, NAME_MAX_LENGTH
from .mixins import NameSlugMixin


from django.core.validators import MaxValueValidator
from datetime import datetime

current_year = datetime.now().year


ROLES = [
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
]


class CustomUser(AbstractUser):
    """Кастомизация модели пользователя."""
    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user',
                            max_length=CHARFIELD_MAX_LENGTH)


class Category(NameSlugMixin):
    """Модель для категорий."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(NameSlugMixin):
    """Модель для жанров."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений."""
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    year = models.IntegerField(
        validators=[MaxValueValidator(current_year)],
        help_text="Введите год не позднее текущего."
    )
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name
