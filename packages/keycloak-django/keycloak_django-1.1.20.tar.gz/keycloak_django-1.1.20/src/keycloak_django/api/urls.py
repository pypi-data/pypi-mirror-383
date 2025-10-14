from django.urls import path
from . import viewsets

urlpatterns = [
    path('roles-permissions/', viewsets.RolesPermissionsViewSet.as_view(), name='roles_permissions'),
]
