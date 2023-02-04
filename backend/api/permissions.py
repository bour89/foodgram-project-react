from rest_framework import permissions


class IsAuthorOrAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user and request.user.is_authenticated
                    and (request.user == obj.author
                         or request.user.is_superuser)))
