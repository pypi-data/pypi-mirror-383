from typing import List
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone


def set_profile(user, groups: List[Group], permissions: List[Permission], user_info=None, attributes_fillable: List[str] = []):
    user.last_login = timezone.now()
    user.groups = groups
    user.permissions = permissions
    if user_info:
        user = fill_user_model_keycloak(
            user=user, user_info=user_info, attributes_fillable=attributes_fillable)
    user.save()
    return user


def fill_user_model_keycloak(user, user_info, attributes_fillable):
    """
    Return the User Keycloak model that is active in this project.
    """
    if hasattr(user, 'is_superuser'):
        user.is_superuser = user_info.get('is_superuser', False)
    if hasattr(user, 'is_staff'):
        user.is_staff = user_info.get('is_staff', True)
    if hasattr(user, 'realm_name'):
        user.realm_name = user_info.get('realm_name', 'master')
    for config in attributes_fillable:
        if isinstance(config, tuple):
            if config[1] in user_info:
                setattr(user, config[0], user_info[config[1]])
            continue
        if config in user_info:
            setattr(user, config, user_info[config])
    return user


def get_user_model_keycloak():
    """
    Return the User Keycloak model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.KEYCLOAK['KEYCLOAK_USER_MODEL'], require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "KEYCLOAK_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "KEYCLOAK_USER_MODEL refers to model '%s' that has not been installed" % settings.KEYCLOAK[
                'KEYCLOAK_USER_MODEL']
        )
