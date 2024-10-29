from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import (CreateAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Comment, Genre, Review, Title
from .filters import TitleFilter
from .permissions import AdminOnly, AdminOrReadOnly, AdminModerAuthorOrReadOnly
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          SignUpSerializer,
                          TitleSerializer,
                          TitleWriteSerializer,
                          UserSerializer)
from .viewsets import (CategoryGenreViewset,
                       CommentReviewViewSet,
                       CustomTitleViewSet)

User = get_user_model()
COMPANY_EMAIL_ADRESS = 'email@email.ru'


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
            COMPANY_EMAIL_ADRESS,
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


class UserDetailAPIView(RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов Админа к конкретному пользователю."""
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    queryset = User.objects.all()
    http_method_names = ['get', 'head', 'options', 'patch', 'delete']
    lookup_field = 'username'


class UserSelfAPIView(RetrieveUpdateAPIView):
    """Класс обработки запросов пользователя к своему профилю."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ['get', 'head', 'options', 'patch']

    def get_object(self):
        return self.request.user


class CategoryViewSet(CategoryGenreViewset):
    """Вьюсет для управления объектами модели Post."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewset):
    """Вьюсет для управления объектами модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(CustomTitleViewSet):
    """Вьюсет для управления обьектами модели Title."""

    queryset = Title.objects.all().order_by('name')
    permission_classes = (AdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleWriteSerializer


class ReviewViewSet(CommentReviewViewSet):
    """Представление для отзывов."""

    serializer_class = ReviewSerializer

    def get_title(self):
        """Получение произведения из аргумента URL."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """Переопределение функции для фильтрации обзоров по произведению."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Переопределение функции для добавления атрибутов."""
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def perform_update(self, serializer):
        """Переопределение функции для обновления атрибутов."""
        serializer.save(title=self.get_title())


class CommentViewSet(CommentReviewViewSet):
    """Представление для комментариев."""

    serializer_class = CommentSerializer

    def get_review(self):
        """Получение обзора из аргумента URL."""
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, pk=review_id, title=title_id)

    def get_queryset(self):
        """Переопределение функции для фильтрации комментариев по посту."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Переопределение функции для добавления атрибутов."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )

    def perform_update(self, serializer):
        """Переопределение функции для обновления атрибутов."""
        serializer.save(review=self.get_review())
