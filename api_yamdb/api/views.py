from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import (CreateAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          SignUpSerializer,
                          TitleSerializer,
                          TitleWriteSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          YamdbTokenObtainPairViewSerializer)
from .viewsets import (CategoryGenreViewset,
                       CommentReviewViewSet,
                       CustomTitleViewSet,
                       UsersGenericViewSet)

User = get_user_model()


class YamdbTokenObtainPairView(TokenObtainPairView):
    """Расширение класса генерации токена."""
    serializer_class = YamdbTokenObtainPairViewSerializer


class SignUpView(CreateAPIView):
    """Регистрация пользователя."""
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(UsersGenericViewSet):
    """Вьюсет списка пользователей."""
    queryset = User.objects.all().order_by('username')
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserSelfAPIView(RetrieveUpdateAPIView):
    """Класс обработки запросов пользователя к своему профилю."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ['get', 'head', 'options', 'patch']

    def get_object(self):
        return self.request.user


class CategoryViewSet(CategoryGenreViewset):
    """Вьюсет для управления объектами модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewset):
    """Вьюсет для управления объектами модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(CustomTitleViewSet):
    """Вьюсет для управления обьектами модели Title."""

    queryset = Title.objects.all().order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
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
        return title.reviews.all().order_by('pub_date')

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
        return review.comments.all().order_by('pub_date')

    def perform_create(self, serializer):
        """Переопределение функции для добавления атрибутов."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )

    def perform_update(self, serializer):
        """Переопределение функции для обновления атрибутов."""
        serializer.save(review=self.get_review())
