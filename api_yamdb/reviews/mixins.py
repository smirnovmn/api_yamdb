from django.db import models
from django.core.validators import RegexValidator

from .constants import (
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH
)


class NameSlugMixin(models.Model):
    """Миксин для моделей с полями name и slug."""
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(
        unique=True,
        max_length=SLUG_MAX_LENGTH,
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message='Поле может содержать только латинские буквы, '
                        'цифры, "-", и "_"',
                code='invalid_name'
            ),
        ]
    )

    class Meta:
        abstract = True
