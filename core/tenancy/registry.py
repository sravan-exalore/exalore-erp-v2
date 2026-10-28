from copy import deepcopy

from django.conf import settings


def register_tenant_database(tenant):
    alias = tenant.db_alias

    if alias in settings.DATABASES:
        return alias

    config = deepcopy(settings.DATABASES["default"])

    config.update(
        {
            "NAME": tenant.db_name,
            "USER": tenant.db_user,
            "PASSWORD": tenant.db_password,
            "HOST": tenant.db_host,
            "PORT": tenant.db_port,
        }
    )

    settings.DATABASES[alias] = config

    return alias
