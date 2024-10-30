import re

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Обработка запроса на регистрацию пользователя."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = ('username', 'email',)

    def validate(self, data):
        """Валидация запроса на регистрацию пользователя."""
        if not re.match(r'^[\w.@+-]+\Z', data['username']):
            raise serializers.ValidationError(
                'В поле username могут быть использованы цифры, буквы, ',
                'нижнее подчеркивание, знаки минуса или плюса.'
            )
        if 'email' not in data or 'username' not in data:
            raise serializers.ValidationError(
                'Поля email и username обязательны для заполнения!'
            )
        if data['email'] == data['username']:
            raise serializers.ValidationError(
                'Значения в полях email и username должны отличаться!'
            )
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени!'
            )

        user_email = User.objects.filter(email=data['email']).first()
        user_username = User.objects.filter(username=data['username']).first()

        if user_email and user_email.username != data['username']:
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегестрирован!'
            )

        if user_username and user_username.email != data['email']:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегестрирован!'
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate(self, data):
        """Валидация запроса к модели пользователя."""
        if self.context['request'].method == 'PATCH':
            user = self.context['request'].user
            if 'role' in data and not user.role == 'admin':
                raise serializers.ValidationError(
                    'Только Администратор может изменять роль пользователя!'
                )
            return data

        if 'email' not in data:
            raise serializers.ValidationError(
                'Поле email не может быть пустым!'
            )

        user_email = User.objects.filter(email=data['email']).first()

        if user_email:
            raise serializers.ValidationError(
                'Пользователь с указанным email уже существует!'
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

    def validate(self, data):
        """Дополнительная валидация пары автор отзыва / произведение."""
        title_id = self.context['view'].kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user
        if self.context['request'].method == 'POST':
            try:
                obj = Review.objects.get(
                    author=author,
                    title=title
                )
            except: 
                return data
            raise serializers.ValidationError(
                'Пользователь может оставить только 1 отзыв на произведение!'
            )
        return super().validate(data)

    class Meta:
        """Метаданные сериализатора."""

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        extra_kwargs = {
            'title': {'write_only': True}
        }


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
