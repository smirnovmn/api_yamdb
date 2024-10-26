from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import AdminOrReadOnly


class CategoryGenreViewset(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для управления объектами моделей Category и Genre."""

    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name', )


class CustomTitleViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):

    pass
