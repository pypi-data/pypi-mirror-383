from django.contrib.auth.models import Group, Permission
from typing import List
from django.contrib.contenttypes.models import ContentType


class GroupsPermissions:
    roles = []
    permissions = []

    def __init__(self, roles: List[str]) -> None:
        self.roles = [rol.replace('_role', '') for rol in list(
            set(roles)) if rol.endswith('_role')]
        self.permissions = [
            permission.replace('_permission', '') for permission in roles if permission.endswith('_permission')]

    def get_roles(self) -> List[Group]:
        roles_available = [Group(name=rol) for rol in self.roles]
        return roles_available

    def get_permissions(self) -> List[Permission]:
        ct = ContentType(app_label='permission', model='account')
        permissions_available = [Permission(
            name=permission, codename=permission, content_type=ct) for permission in self.permissions]
        return permissions_available

    def get_permissions_in_user(self) -> List[Permission]:
        return self.get_permissions()
