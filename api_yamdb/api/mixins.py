import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserValidationMixin(serializers.Serializer):
    """Миксин. Валидация данных пользователя."""

    def validate(self, data):
        """Валидация запроса на регистрацию пользователя."""
        if not re.match(r'^[\w.@+-]+\Z', data['username']):
            raise serializers.ValidationError(
                'В поле username могут быть использованы цифры, буквы, ',
                'нижнее подчеркивание, знаки минуса или плюса.'
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
