import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Обработка запроса на регистрацию пользователя."""
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    class Meta:
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
