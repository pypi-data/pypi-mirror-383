import json

from django.db.models import QuerySet

from ..keycloak import get_default_master_keycloak_admin


def get_base_user(user_model, password):
    return {
        "id": str(user_model.id),
        "email": user_model.email,
        "emailVerified": user_model.email_verified,
        "enabled": user_model.is_active if hasattr(user_model, 'is_active') else True,
        "firstName": user_model.first_name,
        "lastName": user_model.last_name,
        "username": user_model.username,
        "attributes": {
            "is_staff": user_model.is_staff,
            "is_superuser": user_model.is_superuser,
            "employee_id": user_model.employee_id
        },
        "credentials": [{
            "type": "password",
            "value": password,
            "temporary": False
        }]
    }


def create_user_by_owner(user_model, password):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)
    payload = get_base_user(user_model, password)
    keycloak_admin.create_user(payload=payload)
    return keycloak_admin.get_user_id(user_model.username)


def create_user_by_master(user_model, password):
    keycloak_admin = get_default_master_keycloak_admin()
    payload = get_base_user(user_model, password)
    keycloak_admin.create_user(payload=payload)


def update_user(user_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)
    payload = get_base_user(user_model, user_model.password)
    payload.pop('credentials')
    keycloak_admin.update_user(user_id=user_model.pk, payload=payload)


def get_roles_representation(role_names, client_id, keycloak_admin):
    roles_representations = keycloak_admin.get_client_roles(client_id=client_id)
    return [r for r in roles_representations if r['name'] in role_names]

def delete_all_roles_user(user_id, client_id, realm_name):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=realm_name)
    roles = keycloak_admin.get_client_roles_of_user(user_id, client_id)
    keycloak_admin.delete_client_roles_of_user(user_id=user_id, client_id=client_id, roles=roles)

def assign_client_role_to_user(user_model, role_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)

    if not isinstance(role_model, QuerySet):
        roles = [f"{role_model.role.name.replace(' ', '_').lower()}_role"]
    else:
        roles = [f"{r.role.name.replace(' ', '_').lower()}_role" for r in role_model]

    client_id = keycloak_admin.get_client_id(
        client_id=role_model[0].apps_owner.app.client_id)
    delete_all_roles_user(user_id=str(user_model.id), client_id=client_id, realm_name=user_model.realm_name)
    roles = get_roles_representation(role_names=roles, client_id=client_id, keycloak_admin=keycloak_admin)
    keycloak_admin.assign_client_role(user_id=str(user_model.id), client_id=client_id, roles=roles)


def get_base_business_unit(business_units_model):
    business_unit_dict = {
        "id": business_units_model.id,
        "name": business_units_model.name
    }
    return json.dumps(business_unit_dict)


def get_attributes(user_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)
    user_representation = keycloak_admin.get_user(user_id=str(user_model.id))
    if not 'attributes' in user_representation:
        return {}
    return user_representation['attributes']


def assign_business_units_to_user(user_model, business_units):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)
    attributes = get_attributes(user_model)
    # if not 'business_units' in attributes:
    #     attributes['business_units'] = []
    attributes['business_units'] = business_units
    payload = {
        "attributes": {
            **attributes
        }
    }
    keycloak_admin.update_user(user_id=str(user_model.id), payload=payload)


def delete_business_units_to_user(user_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)
    attributes = get_attributes(user_model)
    if 'business_units' in attributes:
        attributes.pop('business_units')
    payload = {
        "attributes": {
            **attributes
        }
    }
    keycloak_admin.update_user(user_id=str(user_model.id), payload=payload)


def delete_user_by_owner(user_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user_model.realm_name)
    keycloak_admin.delete_user(user_id=user_model.id)