import logging
import threading
from django.conf import settings
from django.db import connections

logger = logging.getLogger(__name__)

_lock = threading.Lock()


def ensure_tenant_loaded(db_alias: str) -> bool:
    """
    Thread-safe lazy-loader for tenant database connections.
    Loads tenant config from default database if not already registered in settings.DATABASES.
    """
    if not db_alias or db_alias == "default":
        return True

    if db_alias in settings.DATABASES and db_alias in connections.databases:
        return True

    with _lock:
        if db_alias in settings.DATABASES and db_alias in connections.databases:
            return True

        from .models import Tenant

        try:
            tenant = Tenant.objects.using("default").get(
                db_alias=db_alias,
                is_active=True,
            )
        except Tenant.DoesNotExist:
            logger.warning("Active tenant database '%s' not found", db_alias)
            return False
        except Exception as exc:
            logger.exception("Error querying tenant database '%s': %s", db_alias, exc)
            return False

        conn_max_age = getattr(
            settings,
            "TENANT_CONN_MAX_AGE",
            settings.DATABASES.get("default", {}).get("CONN_MAX_AGE", 60),
        )

        config = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": tenant.db_name,
            "USER": tenant.db_user,
            "PASSWORD": tenant.get_decrypted_password(),
            "HOST": tenant.db_host,
            "PORT": tenant.db_port,
            "CONN_MAX_AGE": conn_max_age,
            "OPTIONS": {},
        }

        settings.DATABASES[db_alias] = config
        connections.databases[db_alias] = config

        logger.info("Successfully loaded and registered tenant database '%s'", db_alias)
        return True
