from django.core.management.base import BaseCommand

from core.tenancy.models import Tenant
from core.tenancy.migration_service import MigrationService


class Command(BaseCommand):
    help = "Migrate all active tenant databases"

    def handle(self, *args, **options):
        tenants = Tenant.objects.filter(is_active=True)
        total = tenants.count()
        self.stdout.write(f"Found {total} tenants")
        success = 0
        failed = 0

        for tenant in tenants:
            self.stdout.write("\n--------------------------------")
            self.stdout.write(f"Migrating: {tenant.db_alias}")

            try:
                MigrationService.migrate_tenant(tenant)
                success += 1
                self.stdout.write(self.style.SUCCESS(f"{tenant.db_alias} completed"))

            except Exception as e:
                failed += 1

                self.stdout.write(self.style.ERROR(f"{tenant.db_alias} failed"))
                self.stdout.write(str(e))

        self.stdout.write("\n==============================")
        self.stdout.write(f"Success: {success}")
        self.stdout.write(f"Failed: {failed}")
