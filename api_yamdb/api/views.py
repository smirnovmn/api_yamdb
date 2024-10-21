from reviews.models import Category, CustomUser

from .serializers import CategorySerializer, UserSerializer

from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from .permissions import AdminOrReadOnly

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для управления объектами модели CustomUser."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления объектами модели Post."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    # pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )

