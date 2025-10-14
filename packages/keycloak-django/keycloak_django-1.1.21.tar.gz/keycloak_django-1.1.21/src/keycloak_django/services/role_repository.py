from ..keycloak import get_default_master_keycloak_admin


def create_role_by_owner(role_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=role_model.owner.realm)
    payload = {
        "id": str(role_model.id),
        "name": role_model.role.name.replace(' ', '_').lower() + '_role',
        "description": role_model.role.description,
        "clientRole": False,
        "attributes": {
            "is_editable": [role_model.role.is_editable],
            "is_role": [True]
        }
    }
    keycloak_admin.create_realm_role(payload=payload)


def create_role_by_app(role_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=role_model.apps_owner.owner.realm)
    payload = {
        "id": str(role_model.id),
        "name": role_model.role.name.replace(' ', '_').lower() + '_role',
        "description": role_model.role.description,
        "clientRole": True,
        "attributes": {
            "is_editable": [role_model.role.is_editable],
            "is_role": [True]
        }
    }
    client_role_id = keycloak_admin.get_client_id(
        client_id=role_model.apps_owner.app.client_id)
    keycloak_admin.create_client_role(
        client_role_id=client_role_id, payload=payload)


def delete_role_by_owner(role_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=role_model.owner.realm)
    keycloak_admin.delete_realm_role(role_name=f"{role_model.role.name.replace(' ', '_').lower()}_role")


def delete_role_by_app(role_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=role_model.apps_owner.owner.realm)
    client_role_id = keycloak_admin.get_client_id(
        client_id=role_model.apps_owner.app.client_id)
    keycloak_admin.delete_client_role(client_role_id=client_role_id,role_name=f"{role_model.role.name.replace(' ', '_').lower()}_role")