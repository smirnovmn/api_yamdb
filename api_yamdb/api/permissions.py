from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Доступ разрешен только администратору."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.role == 'admin'
                    or request.user.is_superuser)


class AdminModerOrReadOnly(permissions.BasePermission):
    """
    Изменение доступно администратору, модератору,
    чтение доступно авторизованному пользователю.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.role == 'admin'
                or request.user.role == 'moderator'
                or request.user.is_superuser
                or request.method in permissions.SAFE_METHODS
            )
