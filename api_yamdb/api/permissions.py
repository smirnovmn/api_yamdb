from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ на чтение и изменение разрешен только администратору."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAdminOrReadOnly(IsAdmin):
    """Всем доступно чтение, создание и изменение - администратору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsAdminModerAuthorOrReadOnly(permissions.BasePermission):
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
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user == obj.author
                or request.user.is_admin
                or request.user.is_moderator
            )
        )
