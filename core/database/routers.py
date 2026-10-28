from core.database.context import get_current_database

DEFAULT_APPS = {
    "authentication",
    "tenancy",
}


TENANT_APPS = {
    "inventory",
    "sales",
    "purchase",
    "accounts",
    "hr",
    "general",
}


class TenantRouter:
    def db_for_read(self, model, **hints):
        app = model._meta.app_label
        if app in DEFAULT_APPS:
            return "default"

        if app in TENANT_APPS:
            db = get_current_database()
            if not db:
                raise RuntimeError("Tenant database context missing")

            return db
        return "default"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._state.db == obj2._state.db:
            return True

        return False

    def allow_migrate(self, db, app_label, **hints):
        if app_label in DEFAULT_APPS:
            return db == "default"

        if app_label in TENANT_APPS:
            return db != "default"

        return db == "default"
