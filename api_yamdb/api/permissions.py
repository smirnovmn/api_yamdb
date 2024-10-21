from rest_framework import permissions


# class AdminOrReadOnly(permissions.BasePermission):
#     """Пермишн для проверки администратора."""

#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.role == 'admin' or request.user.is_superuser
#         )

# class AdminOrReadOnly(permissions.BasePermission):
#     """
#     Изменение доступно администратору,
#     чтение доступно авторизованному пользователю.
#     """

#     def has_permission(self, request, view):
#         # Разрешаем чтение для всех (включая неавторизованных пользователей)
#         if request.method in permissions.SAFE_METHODS:
#             return True

#         # Изменение данных доступно только администраторам
#         return (
#             request.user.is_authenticated
#             and (request.user.role == 'admin' or request.user.is_superuser)
#         )

# class AdminOrReadOnly(permissions.BasePermission):
#     """
#     Изменение доступно администратору, модератору,
#     чтение доступно авторизованному пользователю.
#     """

#     def has_permission(self, request, view):
#         if request.user.is_authenticated:
#             return (
#                 request.user.role == 'admin'
#                 or request.user.is_superuser
#                 or request.method in permissions.SAFE_METHODS
#             )

class AdminOrReadOnly(permissions.BasePermission):
    """Всем доступно чтение, создание и изменение - администратору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == 'admin'
            or request.user.is_superuser
        )
