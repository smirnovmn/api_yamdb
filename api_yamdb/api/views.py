from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters
from rest_framework import status
from rest_framework.generics import (CreateAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .mixins import RestrictPutMixin
from .permissions import AdminOnly
from .serializers import UserSerializer, SignUpSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный класс для генерации токена."""

    def handle_exception(self, exc):
        """Обработка ошибок запроса на создание пользователя."""

        if 'username' not in self.request.data:
            return Response(
                'Пользователь не указан!',
                status=status.HTTP_400_BAD_REQUEST
            )

        username = self.request.data['username']

        if not User.objects.filter(username=username).exists():
            return Response(
                'Пользователь не найден!',
                status=status.HTTP_404_NOT_FOUND
            )

        user = User.objects.get(username=username)
        confirmation_code = self.request.data['confirmation_code']

        if not confirmation_code or not default_token_generator.check_token(
            user, confirmation_code
        ):
            return Response(
                'Неверный код подтверждения!',
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().handle_exception(exc)


class SignUpView(CreateAPIView):
    """Регистрация пользователя."""
    permission_classes = (AllowAny,)

    def generate_confirmation_code(self, user):
        """Генерация уникального кода подтверждения."""
        return default_token_generator.make_token(user)

    def send_confirmation_code(self, username, email):
        """Отправка кода подтверждения на email."""
        user = User.objects.get(username=username)
        confirmation_code = self.generate_confirmation_code(user)
        send_mail(
            'Подтверждение регистрации в YaMDB',
            (f'Пользователь: {username}.'
             f'Ваш код подтверждения: {confirmation_code}.'),
            'email@email.ru',
            [email]
        )

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            existing_user = User.objects.filter(username=username).first()

            if not existing_user:
                serializer.save()

            self.send_confirmation_code(username, email)

            return Response(serializer.validated_data,
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UsersAPIView(ListCreateAPIView):
    """Класс обработки запросов Админа к списку пользователей."""
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UserDetailAPIView(RestrictPutMixin, RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов Админа к конкретному пользователю."""
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    queryset = User.objects.all()
    lookup_field = 'username'


class UserSelfAPIView(RestrictPutMixin, RetrieveUpdateAPIView):
    """Класс обработки запросов пользователя к своему профилю."""
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
