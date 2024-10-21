from rest_framework import serializers
from reviews.models import Category, CustomUser


# class UserSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели CustomUser."""

#     posts = serializers.StringRelatedField(many=True, read_only=True)

#     class Meta:
#         model = CustomUser
#         fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'role')
#         ref_name = 'ReadOnlyUsers'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""

    class Meta:
        model = CustomUser
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

        user_email = CustomUser.objects.filter(email=data['email']).first()

        if user_email:
            raise serializers.ValidationError(
                'Пользователь с указанным email уже существует!'
            )

        return data
