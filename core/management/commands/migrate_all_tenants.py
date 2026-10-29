from django.core.management.base import BaseCommand
from core.tenancy.models import Tenant
from core.tenancy.migration_service import MigrationService


class Command(BaseCommand):
    help = "Run pending migrations across all active tenant databases with enterprise reporting."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show tenant databases that would be migrated without applying changes.",
        )
        parser.add_argument(
            "--stop-on-error",
            action="store_true",
            help="Halt migration sequence immediately if any tenant fails.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        stop_on_error = options.get("stop_on_error", False)

        tenants = Tenant.objects.filter(is_active=True).order_by("id")
        total = tenants.count()
        self.stdout.write(f"Initiating migration scan. Found {total} active tenant(s).\n")

        if dry_run:
            for tenant in tenants:
                self.stdout.write(f"  [DRY RUN] Would migrate: {tenant.db_alias} ({tenant.company_name})")
            return

        success = 0
        failed = 0
        failed_tenants = []

        for index, tenant in enumerate(tenants, 1):
            self.stdout.write(f"[{index}/{total}] Migrating tenant: {tenant.db_alias} ... ", ending="")
            self.stdout.flush()

            try:
                MigrationService.migrate_tenant(tenant)
                success += 1
                self.stdout.write(self.style.SUCCESS("OK"))
            except Exception as e:
                failed += 1
                failed_tenants.append((tenant.db_alias, str(e)))
                self.stdout.write(self.style.ERROR("FAILED"))
                self.stdout.write(self.style.NOTICE(f"    Error: {e}"))

                if stop_on_error:
                    self.stdout.write(self.style.ERROR("\nAborting remaining migrations due to --stop-on-error flag."))
                    break

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"Migration Summary: Total={total} | Succeeded={success} | Failed={failed}")
        if failed_tenants:
            self.stdout.write(self.style.ERROR("\nFailed Databases:"))
            for alias, err in failed_tenants:
                self.stdout.write(self.style.ERROR(f"  - {alias}: {err}"))
        self.stdout.write("=" * 50)
