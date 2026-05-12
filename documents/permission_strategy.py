from rest_framework import permissions
from accounts.models import UserRole


class BaseStrategy:
    def check_permission(self, request, view) -> bool:
        return False

class AdminStrategy(BaseStrategy):
    def check_permission(self, request, view) -> bool:
        return True

class EditorStrategy(BaseStrategy):
    def check_permission(self, request, view) -> bool:
        if request.method == 'DELETE':
            return False
        return True

class ViewerStrategy(BaseStrategy):
    def check_permission(self, request, view) -> bool:
        return request.method in permissions.SAFE_METHODS


class DefaultDenyStrategy(BaseStrategy):
    def check_permission(self, request, view) -> bool:
        return False

class PermissionStrategyFactory:
    _strategies = {
        UserRole.ADMIN.value: AdminStrategy(),
        UserRole.EDITOR.value: EditorStrategy(),
        UserRole.VIEWER.value: ViewerStrategy(),
    }

    @classmethod
    def get_strategy(cls, role: str) -> BaseStrategy:
        return cls._strategies.get(role, DefaultDenyStrategy())
