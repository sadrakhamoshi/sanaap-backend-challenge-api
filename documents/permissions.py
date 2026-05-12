from rest_framework import permissions
from documents.permission_strategy import (
    PermissionStrategyFactory
)

class DocumentRolePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        strategy = PermissionStrategyFactory.get_strategy(request.user.role)
        return strategy.check_permission(request, view)
   