from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core.tenancy.models import Tenant

from core.tenancy.migration_service import MigrationService


class Command(BaseCommand):
    help = "Migrate one tenant"

    def add_arguments(self, parser):
        parser.add_argument("alias")

    def handle(self, *args, **options):
        alias = options["alias"]

        try:
            tenant = Tenant.objects.get(
                db_alias=alias,
                is_active=True,
            )

        except Tenant.DoesNotExist:
            raise CommandError(f"Tenant '{alias}' not found.")

        MigrationService.migrate_tenant(tenant)

        self.stdout.write(self.style.SUCCESS(f"{alias} migrated."))
