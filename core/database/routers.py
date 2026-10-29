import logging
from django.conf import settings
from core.database.context import get_current_database

logger = logging.getLogger(__name__)


class TenantRouter:
    """
    Routes database queries to either the 'default' management database or
    the active tenant-specific database based on the app_label.
    """

    def db_for_read(self, model, **hints):
        app = model._meta.app_label
        if app in settings.DEFAULT_APPS:
            return "default"

        if app in settings.TENANT_APPS:
            db = get_current_database()
            if not db:
                raise RuntimeError(
                    f"Tenant database context missing for tenant-scoped model '{model.__name__}' "
                    f"in app '{app}'. Ensure request is authenticated with a tenant context."
                )
            return db

        # Standard Django contrib apps (auth, contenttypes, sessions, admin) go to default
        return "default"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Only allow relations between objects residing on the exact same physical database.
        Strictly prevents cross-database foreign keys.
        """
        db1 = getattr(obj1._state, "db", None)
        db2 = getattr(obj2._state, "db", None)

        if db1 and db2 and db1 != db2:
            return False

        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure default apps only migrate onto 'default' DB,
        and tenant apps only migrate onto tenant databases.
        """
        if app_label in settings.DEFAULT_APPS:
            return db == "default"

        if app_label in settings.TENANT_APPS:
            return db != "default"

        # Django contrib apps migrate only on default database
        return db == "default"
