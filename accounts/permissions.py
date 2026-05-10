from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsEditorRole(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Editors cannot delete
        if request.method == 'DELETE':
            return False
            
        return bool(request.user.is_admin or request.user.is_editor)

class IsViewerRole(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        # Viewers can only use safe methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
            
        return bool(request.user.is_admin or request.user.is_editor)