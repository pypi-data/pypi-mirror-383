from ..keycloak import get_default_master_keycloak_admin


def get_payload_data(client_model, id):
    payload = dict(client_model.base_config)
    if id:
        payload['id'] = str(id)
    payload['clientId'] = client_model.client_id
    payload['name'] = client_model.name
    payload['rootUrl'] = client_model.rootUrl
    payload['baseUrl'] = client_model.baseUrl
    payload['enabled'] = client_model.active
    payload['publicClient'] = not client_model.is_api
    if not client_model.is_api:
        payload['redirectUris'] = client_model.redirectUris.split(",")
        payload['webOrigins'] = client_model.webOrigins.split(",")
        payload['attributes']['post.logout.redirect.uris'] = "##".join(client_model.logoutUris.split(","))
    return payload


def create_client_by_app_owner(client_model, realm_model, id=None):
    keycloak_admin = get_default_master_keycloak_admin()
    payload = get_payload_data(client_model, id)
    keycloak_admin.create_client_by_realm_name(realm_name=realm_model.realm, payload=payload)

    if client_model.is_api:
        keycloak_admin.set_realm_name(realm_name=realm_model.realm)
        client_id = keycloak_admin.get_client_id(client_model.client_id)
        keycloak_admin.generate_client_secrets(client_id=client_id)


def update_client_by_app_owner(client_model, realm_model, id=None):
    keycloak_admin = get_default_master_keycloak_admin()
    payload = get_payload_data(client_model, id)
    keycloak_admin.update_client_by_realm_name(realm_name=realm_model.realm, payload=payload)

    if client_model.is_api:
        keycloak_admin.set_realm_name(realm_name=realm_model.realm)
        client_id = keycloak_admin.get_client_id(client_model.client_id)
        keycloak_admin.generate_client_secrets(client_id=client_id)


def delete_client_by_app_owner(client_model, realm_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=realm_model.realm)
    client_id = keycloak_admin.get_client_id(client_model.client_id)
    keycloak_admin.delete_client(client_id=client_id)