from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Доступ на чтение и изменение разрешен только администратору."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.role == 'admin'
                    or request.user.is_superuser)


class AdminOrReadOnly(permissions.BasePermission):
    """Всем доступно чтение, создание и изменение - администратору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.role == 'admin'
                or request.user.is_superuser))
        )


class AdminModerAuthorOrReadOnly(permissions.BasePermission):
    """
    Всем доступно чтение, создание доступно аутентифицированным,
    изменение доступно администратору, модератору, автору.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            or request.user.role == 'admin'
            or request.user.role == 'moderator'
            or request.user.is_superuser
        )
