from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ..services.realm_repository import get_apps_login_by_owner


class RolesPermissionsViewSet(APIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        roles = set([group.name for group in user.groups])
        permissions = set([permission.name for permission in user.permissions])
        clients = get_apps_login_by_owner(user=user)
        apps = [{"client_id": client["clientId"], "name": client["name"], "url": client["baseUrl"]}
                for client in clients]
        data = {
            'roles': list(roles),
            'permissions': list(permissions),
            'apps': apps,
            'realm_name': user.realm_name
        }
        return Response(data=data, status=status.HTTP_200_OK)
