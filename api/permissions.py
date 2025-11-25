# permissions.py
from rest_framework.permissions import BasePermission

class IsSuperUserOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Superuser can do anything
        if request.user.is_superuser:
            return True
        # Users can only see their own user object
        return obj == request.user

class IsOwnerOrSuperUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Superuser can access all
        if request.user.is_superuser:
            return True
        # User can access only their inventory
        return obj.user == request.user
