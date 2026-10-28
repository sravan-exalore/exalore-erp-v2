from django.core.management.base import BaseCommand

from core.tenancy.migration_service import MigrationService


class Command(BaseCommand):
    help = "Migrate the core database"

    def handle(self, *args, **options):
        MigrationService.migrate_default()
        self.stdout.write(self.style.SUCCESS("Default database migrated."))
