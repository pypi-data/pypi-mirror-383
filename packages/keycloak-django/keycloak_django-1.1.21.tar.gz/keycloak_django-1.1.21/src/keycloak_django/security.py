from rest_framework import permissions
from django.core.exceptions import PermissionDenied
from typing import List


class ValidatePermissions(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def _has_list_has_permissions(self, permissions_list: List, request, view):
        for per in permissions_list:
            if not (
                    per().has_permission(request, view) if (
                        callable(per) and 'has_permission' in dir(per())) else request.user.has_perm(per)):
                return False
        return True

    def _validate_permission(self, permission, request, view):
        if callable(permission) and 'has_permission' in dir(permission()):
            return permission().has_permission(request, view)

        if isinstance(permission, str):
            return request.user.has_perm(permission)

        if not permission and isinstance(permission, List):
            return True

        if permission and isinstance(permission, List):
            return self._has_list_has_permissions(permission, request, view)

        return False

    def has_permission(self, request, view):
        valid = False
        if request.user and request.user.is_authenticated and hasattr(view,
                                                                      'validate_permissions') and view.validate_permissions:
            if isinstance(view.validate_permissions, str) or isinstance(view.validate_permissions, List) or callable(
                    view.validate_permissions) and 'has_permission' in dir(view.validate_permissions()):
                permission = view.validate_permissions
            else:
                if not hasattr(view, 'action'):
                    view.action = request.method
                view.action = view.action.lower()
                if not view.action in view.validate_permissions:
                    return True
                permission = view.validate_permissions[view.action]
            valid = self._validate_permission(permission, request, view)

        # In case the 403 handler should be called raise the exception
        if hasattr(view, 'raise_exception_validate') and view.raise_exception_validate and not valid:
            raise PermissionDenied
        return valid


def single_permission(permission: str):
    class C(permissions.BasePermission):
        def has_permission(self, request, view):
            if request.user and request.user.is_authenticated:
                return request.user.has_perm(permission)
            return False

    return C


def single_group(group: str):
    class C(permissions.BasePermission):
        def has_permission(self, request, view):
            if request.user and request.user.is_authenticated:
                return group in [g.name for g in request.user.groups.all()]
            return False

    return C
