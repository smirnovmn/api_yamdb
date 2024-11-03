from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from .mixins import UserValidationMixin
from .constants import (EMAIL_MAX_LENGTH,
                        CHARFIELD_MAX_LENGTH,
                        SCORE_MAX_VALUE,
                        SCORE_MIN_VALUE)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()
COMPANY_EMAIL_ADRESS = settings.COMPANY_EMAIL_ADRESS


class SignUpSerializer(UserValidationMixin):
    """Обработка запроса на регистрацию пользователя."""

    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH, required=True
    )
    username = serializers.CharField(
        max_length=CHARFIELD_MAX_LENGTH, required=True
    )

    def generate_confirmation_code(self, user):
        """Генерация уникального кода подтверждения."""
        return default_token_generator.make_token(user)

    def send_confirmation_code(self, user, email):
        """Отправка кода подтверждения на email."""
        confirmation_code = self.generate_confirmation_code(user)
        send_mail(
            'Подтверждение регистрации в YaMDB',
            (f'Пользователь: {user.username}.'
             f'Ваш код подтверждения: {confirmation_code}.'),
            COMPANY_EMAIL_ADRESS,
            [email]
        )

    def create(self, validated_data):
        """Создание нового пользователя."""
        username = validated_data.get('username')
        email = validated_data.get('email')

        if User.objects.filter(username=username).exists():
            current_user = User.objects.get(username=username)
        else:
            current_user = User.objects.create_user(**validated_data)

        self.send_confirmation_code(current_user, email)
        return current_user


class YamdbTokenObtainPairViewSerializer(serializers.Serializer):
    """Обработка запроса на генерацию токена."""
    username = serializers.CharField(
        max_length=CHARFIELD_MAX_LENGTH, required=True
    )
    confirmation_code = serializers.CharField(
        max_length=CHARFIELD_MAX_LENGTH, required=True
    )

    def validate(self, data):
        """Валидация запроса на генерацию токена."""
        username = data['username']
        confirmation_code = data['confirmation_code']

        if not User.objects.filter(username=username).exists():
            raise NotFound(
                'Пользователь не найден!'
            )

        user = User.objects.get(username=username)
        if not confirmation_code or not default_token_generator.check_token(
            user, confirmation_code
        ):
            raise serializers.ValidationError(
                'Неверный код подтверждения!'
            )

        return data


class UserCreateSerializer(serializers.ModelSerializer, UserValidationMixin):
    """Сериализатор создания нового пользователя."""

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        ordering = ('username')

    def validate(self, data):
        """Валидация запроса к модели пользователя."""

        if 'email' not in data:
            raise serializers.ValidationError(
                'Поле email не может быть пустым!'
            )

        data = super().validate(data)
        return data


class UserSerializer(serializers.ModelSerializer, UserValidationMixin):
    """Сериализатор модели пользователя."""

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        ordering = ('username')

    def validate(self, data):
        """Валидация запроса к модели пользователя."""
        if self.context['request'].method == 'PATCH':
            user = self.context['request'].user
            if 'role' in data and not user.is_admin:
                raise serializers.ValidationError(
                    'Только Администратор может изменять роль пользователя!'
                )
            return data


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        """Метаданные сериализатора."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        """Метаданные сериализатора."""

        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для операций чтения модели Title."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        """Метаданные сериализатора."""

        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        """Вычисление среднего рейтинга произведения."""
        if obj.reviews.count() > 0:
            return obj.reviews.aggregate(Avg('score'))['score__avg']
        return None


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для операций записи модели Title."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        """Метаданные сериализатора."""

        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для постов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField()

    class Meta:
        """Метаданные сериализатора."""

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        extra_kwargs = {
            'title': {'write_only': True}
        }

    def validate_score(self, value):
        """Проверка значения оценки произведения."""
        if value < SCORE_MIN_VALUE or value > SCORE_MAX_VALUE:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10!'
            )

    def validate(self, data):
        """Дополнительная проверка на уникальность пары автор+произведение."""
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs['title_id']
            title = get_object_or_404(Title, pk=title_id)
            author = self.context['request'].user
            if Review.objects.filter(
                author=author,
                title=title
            ).exists():
                raise serializers.ValidationError(
                    'Пользователь может оставить'
                    'только 1 отзыв на произведение!'
                )
        return super().validate(data)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    review = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(), default=None)

    class Meta:
        """Метаданные сериализатора."""

        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        read_only_fields = ('review',)
