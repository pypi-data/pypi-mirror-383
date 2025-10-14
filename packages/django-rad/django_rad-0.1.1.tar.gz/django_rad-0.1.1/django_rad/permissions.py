from typing import Callable


class BasePermission:
    def has_permission(self, request, view) -> bool:
        """Global check (before action)"""
        return True

    def has_object_permission(self, request, view, obj) -> bool:
        """Object-level check (after action)"""
        return True


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated


def skip_permissions(func) -> Callable:
    func.skip_perm = True
    return func
