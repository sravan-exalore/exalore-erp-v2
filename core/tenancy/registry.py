import threading
from copy import deepcopy
from django.conf import settings
from django.db import connections

_registry_lock = threading.Lock()


def register_tenant_database(tenant) -> str:
    """
    Registers a tenant database connection in Django's active connection handler.
    Thread-safe and uses decrypted password.
    """
    alias = tenant.db_alias

    if alias in settings.DATABASES and alias in connections.databases:
        return alias

    with _registry_lock:
        if alias in settings.DATABASES and alias in connections.databases:
            return alias

        config = deepcopy(settings.DATABASES["default"])
        config.update(
            {
                "NAME": tenant.db_name,
                "USER": tenant.db_user,
                "PASSWORD": tenant.get_decrypted_password(),
                "HOST": tenant.db_host,
                "PORT": tenant.db_port,
            }
        )

        settings.DATABASES[alias] = config
        connections.databases[alias] = config

        return alias
