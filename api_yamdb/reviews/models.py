from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (CHARFIELD_MAX_LENGTH, NAME_MAX_LENGTH)
from .mixins import NameSlugMixin

current_year = datetime.now().year

ROLES = [
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
]


class YamdbUser(AbstractUser):
    """Кастомизация модели пользователя сервиса YaMDB."""

    bio = models.TextField(blank=True)
    role = models.CharField(choices=ROLES, default='user',
                            max_length=CHARFIELD_MAX_LENGTH)

    @property
    def is_admin(self):
        """Возвращает True, если пользователь Админ или Суперпользователь."""
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        """Возвращает True, если пользователь Модератор."""
        return self.role == 'moderator'


class Category(NameSlugMixin):
    """Модель для категорий."""

    class Meta:
        """Метаданные отзыва."""

        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Строковое представление класса."""
        return self.name


class Genre(NameSlugMixin):
    """Модель для жанров."""

    class Meta:
        """Метаданные отзыва."""

        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        """Строковое представление класса."""
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
        """Метаданные отзыва."""

        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        """Строковое представление класса."""
        return self.name


class Review(models.Model):
    """Модель для отзывов."""

    text = models.TextField()
    author = models.ForeignKey(
        YamdbUser, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        """Метаданные отзыва."""

        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        """Строковое представление класса."""
        return self.text


class Comment(models.Model):
    """Модель для комментариев."""

    text = models.TextField()
    author = models.ForeignKey(
        YamdbUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        """Строковое представление класса."""
        return self.text

    class Meta:
        """Метаданные комментария."""

        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
