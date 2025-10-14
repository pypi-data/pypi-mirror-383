from django.conf import settings
from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .tools import fill_user_model_keycloak, get_user_model_keycloak, set_profile
from keycloak.exceptions import KeycloakInvalidTokenError
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from .keycloak import KeycloakToken
from django.core.cache import cache
from . import KEYCLOAK_TOKEN


class KeycloakMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        """
        :param get_response:
        """

        self.config = settings.KEYCLOAK

        # Read configurations
        try:
            self.server_url = self.config['SERVER_URL']
            self.client_id = self.config['CLIENT_ID']
            self.audience_client = self.config.get(
                'AUDIENCE_CLIENT', self.client_id)
            self.realm = self.config['REALM_NAME']
        except KeyError as e:
            raise Exception(
                "KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")

        self.client_secret_key = self.config.get('CLIENT_SECRET_KEY', None)
        self.client_public_key = self.config.get('PUBLIC_KEY', None)
        self.default_access = self.config.get('DEFAULT_ACCESS', "DENY")
        self.method_validate_token = self.config.get(
            'METHOD_VALIDATE_TOKEN', "INTROSPECT")
        self.keycloak_authorization_config = self.config.get(
            'AUTHORIZATION_CONFIG', None)
        self.create_user_if_not_exist = self.config.get(
            'CREATE_USER_IF_NOT_EXIST', False)
        self.attributes_fillable = self.config.get('ATTRIBUTES_FILLABLE', None)
        self.public_key_validate = self.config.get(
            'PUBLIC_KEY_VALIDATE', 'inter')

        # Create Keycloak instance
        self.keycloak = KeycloakToken(
            client_id=self.client_id, realm_name=self.realm)

        # # Read policies
        # if self.keycloak_authorization_config:
        #     self.keycloak.load_authorization_config(
        #         self.keycloak_authorization_config)

        # Django
        self.get_response = get_response

    def __call__(self, request):
        """
        :param request:
        :return:
        """
        return self.get_response(request)
    
    def is_superuser(self, token_info):
        if token_info['realm_name'] == 'master'and token_info['azp'] == "admin-cli":
            User = get_user_model()
            payload = {
                "id": token_info['sub'],
                "is_superuser": True,
                "is_staff": True,
                "realm_name": 'master',
                "email": 'master@master.com',
                "username": 'master',
            }
            user = User(**payload)
            user.groups = []
            user.permissions = []
            return user
        return None


    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Validate only the token introspect.
        :param request: django request
        :param view_func:
        :param view_args: view args
        :param view_kwargs: view kwargs
        :return:
        """
        # logout(request)

        if 'HTTP_AUTHORIZATION' not in request.META:
            cache.delete(key=KEYCLOAK_TOKEN)
            return None

        token = request.META.get('HTTP_AUTHORIZATION')
        cache.set(key=KEYCLOAK_TOKEN, value=token)
        self.realm = self.config['REALM_NAME']
        try:
            user_groups, user_permissions, user_info = self.keycloak.get_roles_permissions_user(token.replace('Bearer ', ''),
                                                                                                public_key_validate=self.public_key_validate,
                                                                                                method_token_info=self.method_validate_token.lower(),
                                                                                                key=self.client_public_key, audience=self.audience_client)
        except KeycloakInvalidTokenError as e:
            logout(request=request)
            return JsonResponse({"detail": AuthenticationFailed.default_detail},
                                status=AuthenticationFailed.status_code)

        UserModel = get_user_model()
        try:
            superuser = self.is_superuser(user_info)
            if superuser:
                user = superuser
            else:
                user = UserModel.objects.get(id=user_info['sub'])
        except UserModel.DoesNotExist:
            payload = {}
            for config in self.attributes_fillable:
                if isinstance(config, tuple):
                    if config[1] in user_info:
                        payload[config[0]] = user_info[config[1]]
                    continue
                if config in user_info:
                    payload[config] = user_info[config]
            payload['id'] = user_info['sub']
            user = None
            if self.create_user_if_not_exist:
                user = UserModel(**payload)
                if not user.is_superuser:
                    user.save()
            if not user:
                User = get_user_model_keycloak()
                user = User(**payload)
                user.groups = user_groups
                user.permissions = user_permissions
                fill_user_model_keycloak(
                    user=user, user_info=user_info, attributes_fillable=self.attributes_fillable)

        if user and (str(request.path).endswith('roles-permissions/')):
            user = set_profile(
                user=user,
                groups=user_groups,
                permissions=user_permissions,
                user_info=user_info,
                attributes_fillable=self.attributes_fillable
            )
            login(request, user)
        else:
            user.groups = user_groups
            user.permissions = user_permissions
        
        request.user = user

        if self.default_access == "DENY" and (not user_permissions or not user_groups):
            # User Permission Denied
            return JsonResponse({"detail": PermissionDenied.default_detail},
                                status=PermissionDenied.status_code)
        return None

    @property
    def keycloak(self):
        return self._keycloak

    @keycloak.setter
    def keycloak(self, value):
        self._keycloak = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def server_url(self):
        return self._server_url

    @server_url.setter
    def server_url(self, value):
        self._server_url = value

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def create_user_if_not_exist(self):
        return self._create_user_ifnotexist

    @create_user_if_not_exist.setter
    def create_user_if_not_exist(self, value):
        self._create_user_ifnotexist = value

    @property
    def attributes_fillable(self):
        return self._atributes_fillable

    @attributes_fillable.setter
    def attributes_fillable(self, value):
        self._atributes_fillable = value

    @property
    def audience_client(self):
        return self._audience_client

    @audience_client.setter
    def audience_client(self, value):
        self._audience_client = value

    @property
    def client_secret_key(self):
        return self._client_secret_key

    @client_secret_key.setter
    def client_secret_key(self, value):
        self._client_secret_key = value

    @property
    def client_public_key(self):
        return self._client_public_key

    @client_public_key.setter
    def client_public_key(self, value):
        self._client_public_key = value

    @property
    def realm(self):
        return self._realm

    @realm.setter
    def realm(self, value):
        self._realm = value

    @property
    def keycloak_authorization_config(self):
        return self._keycloak_authorization_config

    @keycloak_authorization_config.setter
    def keycloak_authorization_config(self, value):
        self._keycloak_authorization_config = value

    @property
    def method_validate_token(self):
        return self._method_validate_token

    @method_validate_token.setter
    def method_validate_token(self, value):
        self._method_validate_token = value

    @property
    def method_create_user(self):
        return self._method_create_user

    @method_create_user.setter
    def method_create_user(self, value):
        self._method_create_user = value