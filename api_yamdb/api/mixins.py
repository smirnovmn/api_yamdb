from rest_framework.exceptions import MethodNotAllowed


class RestrictPutMixin:
    """Запрет на использование метода PUT."""

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')
