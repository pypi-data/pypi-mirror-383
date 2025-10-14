from ..keycloak import get_default_master_keycloak_admin


def get_permissions_by_app(apps_owners_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=apps_owners_model.owner.realm)
    roles = keycloak_admin.get_client_roles(client_id=apps_owners_model.id)
    return [p for p in roles if p['name'].endswith('_permission')]


def create_permission_by_app(earp_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(
        realm_name=earp_model.app_role.apps_owner.owner.realm)
    permissions = get_permissions_by_app(earp_model.app_role.apps_owner)
    permissions_names = [p['name'] for p in permissions]
    name = earp_model.endpoint.name
    name = name.replace(' ', '_').lower()
    all_permissions = [f'{name}_allow_read_permission',
                       f'{name}_allow_add_permission',
                       f'{name}_allow_delete_permission',
                       f'{name}_allow_update_permission',
                       f'{name}_allow_execute_permission']
    permissions_create = [
        p for p in all_permissions if p not in permissions_names]
    for p in permissions_create:
        payload = {
            "name": p,
            "description": p.replace("_", " "),
            "clientRole": True,
            "attributes": {
                "is_editable": [False],
                "is_role": [False]
            }
        }
        client_role_id = keycloak_admin.get_client_id(
            client_id=earp_model.app_role.apps_owner.app.client_id)
        keycloak_admin.create_client_role(
            client_role_id=client_role_id, payload=payload)


def add_permission_by_role_app(earp_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(
        realm_name=earp_model.app_role.apps_owner.owner.realm)
    permissions = get_permissions_by_app(earp_model.app_role.apps_owner)
    name = earp_model.endpoint.name
    name = name.replace(' ', '_').lower()
    all_permissions = []
    if earp_model.allow_read:
        all_permissions.append(f'{name}_allow_read_permission')
    if earp_model.allow_add:
        all_permissions.append(f'{name}_allow_add_permission')
    if earp_model.allow_delete:
        all_permissions.append(f'{name}_allow_delete_permission')
    if earp_model.allow_update:
        all_permissions.append(f'{name}_allow_update_permission')
    if earp_model.allow_execute:
        all_permissions.append(f'{name}_allow_execute_permission')

    permissions_append = [
        p for p in permissions if p['name'] in all_permissions]
    client_role_id = keycloak_admin.get_client_id(
        client_id=earp_model.app_role.apps_owner.app.client_id)
    role_name = earp_model.app_role.role.name.replace(' ', '_').lower()
    delete_roles = keycloak_admin.get_composite_client_roles_to_role(
        client_role_id=client_role_id, role_name=f'{role_name}_role')
    delete_roles = [r for r in delete_roles if r['name'].startswith(f'{name}_allow')]
    if delete_roles:
        keycloak_admin.remove_composite_client_roles_to_role(
            client_role_id=client_role_id, role_name=f'{role_name}_role', roles=delete_roles)
    keycloak_admin.add_composite_client_roles_to_role(client_role_id=client_role_id, role_name=f'{role_name}_role', roles=permissions_append)


def delete_permission_by_app(earp_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(
        realm_name=earp_model.app_role.apps_owner.owner.realm)
    permissions = get_permissions_by_app(earp_model.app_role.apps_owner)
    permissions_names = [p['name'] for p in permissions]
    name = earp_model.endpoint.name
    all_permissions = [f'{name}_allow_read_permission',
                       f'{name}_allow_add_permission',
                       f'{name}_allow_delete_permission',
                       f'{name}_allow_update_permission',
                       f'{name}_allow_execute_permission']
    permissions_delete = [
        p for p in permissions_names if p in all_permissions]
    client_role_id = keycloak_admin.get_client_id(
        client_id=earp_model.app.client_id)
    for p in permissions_delete:
        keycloak_admin.delete_client_role(client_role_id=client_role_id, role_name=p)

