from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Разрешение доступа только для владельцев объекта"""

    message = 'Вы не являетесь владельцем этой привычки.'

    def has_object_permission(self, request, view, obj) -> bool:
        return request.user == obj.user
