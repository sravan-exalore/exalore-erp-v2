from django.core.management import call_command
from django.conf import settings

from core.tenancy.registry import register_tenant_database


class MigrationService:
    @staticmethod
    def migrate_default():
        call_command("migrate", database="default")

    @staticmethod
    def migrate_tenant(tenant):
        register_tenant_database(tenant)
        for app in settings.TENANT_APPS:
            call_command("migrate", app, database=tenant.db_alias, verbosity=1)
