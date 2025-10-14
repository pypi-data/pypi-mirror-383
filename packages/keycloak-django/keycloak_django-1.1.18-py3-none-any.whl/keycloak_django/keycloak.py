import base64
from django.conf import settings
from keycloak import KeycloakPutError, urls_patterns,  KeycloakOpenID
import json
from typing import List, Dict
from keycloak.keycloak_admin import KeycloakAdmin
from keycloak.exceptions import (
    KeycloakAuthenticationError,
    KeycloakAuthorizationConfigError,
    KeycloakDeprecationError,
    KeycloakGetError,
    KeycloakInvalidTokenError,
    KeycloakPostError,
    KeycloakRPTNotFound,
    raise_error_from_response, KeycloakDeleteError,
)
from jose import jwt
from .groups_permissions import GroupsPermissions


class KeycloakAdminRepository(KeycloakAdmin):

    URL_ADMIN_USER_ROLES = "admin/realms/{realm-name}/users/{id}/role-mappings"

    def __init__(
            self,
            server_url,
            username=None,
            password=None,
            token=None,
            totp=None,
            realm_name="master",
            client_id="admin-cli",
            verify=True,
            client_secret_key=None,
            custom_headers=None,
            user_realm_name=None,
            auto_refresh_token=None,
            timeout=60,
    ):
        KeycloakAdmin.__init__(self, server_url,
                               username,
                               password,
                               token,
                               totp,
                               realm_name,
                               client_id,
                               verify,
                               client_secret_key,
                               custom_headers,
                               user_realm_name,
                               auto_refresh_token,
                               timeout)

    def get_composite_client_roles_to_role(self, client_role_id, role_name, brief_representation=True) -> List[Dict]:
        """Get composite roles to client role.

        Returns a list of roles of which the role in client
        :param client_role_id: id of client (not client-id)
        :type client_role_id: str
        :param role_name: The name of the role
        :type role_name: str
        :param brief_representation: whether to omit attributes in the response
        :type brief_representation: True
        :return: Keycloak server response
        :rtype: bytes
        """
        params_path = {"realm-name": self.realm_name,
                       "id": client_role_id, "role-name": role_name}
        params = {"briefRepresentation": brief_representation}
        data_raw = self.raw_get(
            urls_patterns.URL_ADMIN_CLIENT_ROLES_COMPOSITE_CLIENT_ROLE.format(**params_path), **params
        )
        return raise_error_from_response(data_raw, KeycloakGetError)

    def remove_composite_client_roles_to_role(self, client_role_id, role_name, roles):
        """Remove composite roles from the role.

        :param role_name: The name of the role
        :type role_name: str
        :param client_role_id: id of client (not client-id)
        :type client_role_id: str
        :param roles: roles list or role (use RoleRepresentation) to be removed
        :type roles: list
        :return: Keycloak server response
        :rtype: bytes
        """
        payload = roles if isinstance(roles, list) else [roles]
        params_path = {"realm-name": self.realm_name,
                       "id": client_role_id, "role-name": role_name}
        data_raw = self.raw_delete(
            urls_patterns.URL_ADMIN_CLIENT_ROLES_COMPOSITE_CLIENT_ROLE.format(
                **params_path),
            data=json.dumps(payload),
        )
        return raise_error_from_response(data_raw, KeycloakDeleteError, expected_codes=[204])

    def get_client_secrets_by_realm(self, client_id, realm_name):
        """Get representation of the client secrets.

        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_getclientsecret

        :param client_id:  id of client (not client-id)
        :param realm_name:  name of realm_name (not realm-id)
        :type client_id: str
        :type realm_name: str
        :return: Keycloak server response (ClientRepresentation)
        :rtype: list
        """
        params_path = {"realm-name": realm_name, "id": client_id}
        data_raw = self.raw_get(
            urls_patterns.URL_ADMIN_CLIENT_SECRETS.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_clients_by_realm(self, realm_name):
        """Get clients.

        Returns a list of clients belonging to the realm

        ClientRepresentation
        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_clientrepresentation

        :param realm_name:  name of realm_name (not realm-id)
        :type realm_name: str
        :return: Keycloak server response (ClientRepresentation)
        :rtype: list
        """

        params_path = {"realm-name": realm_name}
        data_raw = self.raw_get(
            urls_patterns.URL_ADMIN_CLIENTS.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_client_id_by_realm(self, client_id, realm_name):
        """Get internal keycloak client id from client-id.

        This is required for further actions against this client.

        :param realm_name:  name of realm_name (not realm-id)
        :param client_id: clientId in ClientRepresentation
            https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_clientrepresentation
        :type client_id: str
        :type realm_name: str
        :return: client_id (uuid as string)
        :rtype: str
        """
        clients = self.get_clients_by_realm(realm_name=realm_name)

        for client in clients:
            if client_id == client.get("clientId"):
                return client["id"]

        return None

    def generate_client_secrets_by_realm(self, client_id, realm_name):
        """Generate a new secret for the client.

        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_regeneratesecret

        :param realm_name:  name of realm_name (not realm-id)
        :param client_id:  id of client (not client-id)
        :type client_id: str
        :type realm_name: str
        :return: Keycloak server response (ClientRepresentation)
        :rtype: bytes
        """
        params_path = {"realm-name": realm_name, "id": client_id}
        data_raw = self.raw_post(
            urls_patterns.URL_ADMIN_CLIENT_SECRETS.format(**params_path), data=None
        )
        return raise_error_from_response(data_raw, KeycloakPostError)

    def create_client_by_realm_name(self, realm_name, payload, skip_exists=False):
        """Create a client.

        ClientRepresentation:
        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_clientrepresentation

        :param skip_exists: If true then do not raise an error if client already exists
        :param realm_name:  name of realm_name (not realm-id)
        :type skip_exists: bool
        :param payload: ClientRepresentation
        :type payload: dict
        :type realm_name: str
        :return: Client ID
        :rtype: str
        """
        if skip_exists:
            client_id = self.get_client_id_by_realm(
                client_id=payload["clientId"], realm_name=realm_name)

            if client_id is not None:
                return client_id

        params_path = {"realm-name": realm_name}
        data_raw = self.raw_post(
            urls_patterns.URL_ADMIN_CLIENTS.format(**params_path), data=json.dumps(payload)
        )
        raise_error_from_response(
            data_raw, KeycloakPostError, expected_codes=[201], skip_exists=skip_exists
        )
        _last_slash_idx = data_raw.headers["Location"].rindex("/")
        return data_raw.headers["Location"][_last_slash_idx + 1:]  # noqa: E203

    def update_client_by_realm_name(self, realm_name, payload, skip_exists=False):
        """Update a client.

        ClientRepresentation:
        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_clientrepresentation

        :param skip_exists: If true then do not raise an error if client already exists
        :param realm_name:  name of realm_name (not realm-id)
        :type skip_exists: bool
        :param payload: ClientRepresentation
        :type payload: dict
        :type realm_name: str
        :return: Client ID
        :rtype: str
        """
        client_id = self.get_client_id_by_realm(
            client_id=payload["clientId"], realm_name=realm_name)
        if client_id is not None:
            payload["id"] = client_id

        params_path = {"realm-name": realm_name, "id": client_id}
        data_raw = self.raw_put(
            urls_patterns.URL_ADMIN_CLIENT.format(**params_path), data=json.dumps(payload)
        )
        return raise_error_from_response(data_raw, KeycloakPutError, expected_codes=[204])

    def set_realm_name(self, realm_name: str) -> None:
        """Create a client.

        ClientRepresentation:
        https://www.keycloak.org/docs-api/18.0/rest-api/index.html#_clientrepresentation

        :param realm_name:  name of realm_name (not realm-id)
        :type realm_name: str
        :return: Client ID
        :rtype: str
        """
        self.realm_name = realm_name

    def _get_roles_of_user(
        self, role_mapping_url, user_id, **params
    ):
        """Get client roles of a single user helper.

        :param client_level_role_mapping_url: Url for the client role mapping
        :type client_level_role_mapping_url: str
        :param user_id: User id
        :type user_id: str
        :param client_id: Client id
        :type client_id: str
        :param params: Additional parameters
        :type params: dict
        :returns: Client roles of a user
        :rtype: list
        """
        params_path = {"realm-name": self.realm_name, "id": user_id}
        data_raw = self.raw_get(
            role_mapping_url.format(**params_path), **params)
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_roles_of_user(self, user_id):
        """Get all roles for a user.

        :param user_id: id of user
        :type user_id: str
        :return: Keycloak server response (array RoleMappingsRepresentation)
        :rtype: list
        """
        return self._get_roles_of_user(
            self.URL_ADMIN_USER_ROLES, user_id
        )
    
    def get_token_master(self):
        """Get master admin token.
        The admin token is then set in the `token` attribute.
        """

        self.keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id="admin-cli",
            realm_name="master",
            verify=self.verify,
            client_secret_key=self.client_secret_key,
            custom_headers=self.custom_headers,
            timeout=50,
        )

        grant_type = ["client_credentials",]

        self.token = self.keycloak_openid.token(
            self.username, self.password, grant_type=grant_type, totp=self.totp
        )
        
        if "access_token" in self.token:
            return self.token["access_token"]

        return self.token


def get_default_keycloak_admin():
    config = settings.KEYCLOAK
    try:
        server_url = config['SERVER_URL']
        client_id = config['CLIENT_ID']
        realm = config['REALM_NAME']
        client_secret_key = config.get('CLIENT_SECRET_KEY', None)

        return KeycloakAdminRepository(server_url=server_url,
                                       realm_name=realm,
                                       client_id=client_id,
                                       client_secret_key=client_secret_key,
                                       user_realm_name=realm,
                                       auto_refresh_token=[
                                           'get', 'put', 'post', 'delete'],
                                       verify=True)
    except KeyError as e:
        raise Exception(
            "KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")


def get_default_master_keycloak_admin(realm=None, client_secret_key=None, client_id=None):
    config = settings.KEYCLOAK
    try:
        server_url = config['SERVER_URL']
        client_id = 'admin-cli' if not client_id else client_id
        realm = 'master' if not realm else realm
        client_secret_key = config.get(
            'ADMIN_CLI_SECRET_KEY', None) if not client_secret_key else client_secret_key

        return KeycloakAdminRepository(server_url=server_url,
                                       realm_name=realm,
                                       client_id=client_id,
                                       client_secret_key=client_secret_key,
                                       user_realm_name=realm,
                                       auto_refresh_token=[
                                           'get', 'put', 'post', 'delete'],
                                       verify=True)
    except KeyError as e:
        raise Exception(
            "KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")


class KeycloakToken:

    def __init__(self, realm_name, client_id):
        self.realm_name = realm_name
        self.client_id = client_id

    def decode_token(self, token, key, algorithms=["RS256"], **kwargs):
        """Decode user token.

        A JSON Web Key (JWK) is a JavaScript Object Notation (JSON) data
        structure that represents a cryptographic key.  This specification
        also defines a JWK Set JSON data structure that represents a set of
        JWKs.  Cryptographic algorithms and identifiers for use with this
        specification are described in the separate JSON Web Algorithms (JWA)
        specification and IANA registries established by that specification.

        https://tools.ietf.org/html/rfc7517

        :param token: Keycloak token
        :type token: str
        :param key: Decode key
        :type key: str
        :param algorithms: Algorithms to use for decoding
        :type algorithms: list[str]
        :param kwargs: Keyword arguments
        :type kwargs: dict
        :returns: Decoded token
        :rtype: dict
        """
        # if 'audience' in kwargs:
        #     self.client_id = kwargs['audience']
        # del kwargs['audience']
        return jwt.decode(token, key, algorithms=algorithms, **kwargs)

    def _token_info(self, token, method_token_info, **kwargs):
        """Getter for the token data.

        :param token: Token
        :type token: str
        :param method_token_info: Token info method to use
        :type method_token_info: str
        :param kwargs: Additional keyword arguments
        :type kwargs: dict
        :returns: Token info
        :rtype: dict
        """
        if method_token_info == "introspect":
            # token_info = self.introspect(token)
            raise NotImplementedError()
        else:
            token_info = self.decode_token(token, **kwargs)

        return token_info

    def get_roles_by_user(self, user_id):
        keycloak_admin = get_default_master_keycloak_admin()
        keycloak_admin.set_realm_name(realm_name=self.realm_name)
        client_id = keycloak_admin.get_client_id(client_id=self.client_id)
        return keycloak_admin.get_client_roles_of_user(user_id, client_id)

    def get_permission_by_role(self, role_name):
        keycloak_admin = get_default_master_keycloak_admin()
        keycloak_admin.set_realm_name(realm_name=self.realm_name)
        client_id = keycloak_admin.get_client_id(client_id=self.client_id)
        return keycloak_admin.get_composite_client_roles_to_role(
            client_role_id=client_id, role_name=role_name)

    def get_key_rsa(self, token):
        try:
            body_json = token.split('.')[1]
            body_token = base64.b64decode(
                body_json + "==" if not body_json.endswith("==") else "")
            body_token = body_token.decode("ascii")
            body_token = json.loads(body_token)
            realm = body_token.get('iss').split('/')[-1]
            self.realm_name = realm
            keycloak_admin = get_default_master_keycloak_admin()
            keycloak_admin.set_realm_name(realm_name=realm)
            keys = keycloak_admin.get_keys()
            active_key = keys['active']['RS256']
            for key in keys['keys']:
                if key['kid'] == active_key:
                    publicKey = f"""-----BEGIN PUBLIC KEY-----
{key['publicKey']}
-----END PUBLIC KEY-----"""
                    return publicKey
            return ''
        except:
            return ''

    def is_superuser(self, token_info):
        return token_info['realm_name'] == 'master'and token_info['azp'] == "admin-cli"

    def get_roles_permissions_user(self, token, public_key_validate='inter', method_token_info="introspect", **kwargs):
        """Get permission by user token.

        :param token: user token
        :type token: str
        :param method_token_info: Decode token method
        :type method_token_info: str
        :param kwargs: parameters for decode
        :type kwargs: dict
        :returns: permissions list
        :rtype: list
        :raises KeycloakAuthorizationConfigError: In case of bad authorization configuration
        :raises KeycloakInvalidTokenError: In case of bad token
        """
        try:
            if public_key_validate == 'auto':
                kwargs['key'] = self.get_key_rsa(token)

            token_info = self._token_info(token, method_token_info, **kwargs)
            realm_name = token_info.get('iss', 'https/master').split('/')[-1]
            token_info['realm_name'] = realm_name
        except Exception as e:
            print(str(e))
            raise KeycloakInvalidTokenError("Token expired or invalid.")

        if method_token_info == "introspect" and not token_info["active"]:
            raise KeycloakInvalidTokenError("Token expired or invalid.")
        
        if self.is_superuser(token_info=token_info):
            roles = []
        else:
            roles = self.get_roles_by_user(token_info['sub'])

        find_permissions = [policies['name']
                            for policies in roles if policies['composite']]
        for role in find_permissions:
            permissions = self.get_permission_by_role(role)
            roles.extend(permissions)

        rolesandpermissions = GroupsPermissions(
            [policies['name'] for policies in roles])

        roles = rolesandpermissions.get_roles()
        permissions = rolesandpermissions.get_permissions_in_user()

        return roles, permissions, token_info
