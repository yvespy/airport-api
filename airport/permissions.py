from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class AdminAllOrIsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS and
            request.user and request.user.is_authenticated
        ) or (
            request.user and request.user.is_staff
        )


class IsAuthenticatedOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
