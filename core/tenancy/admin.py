import logging
from django.contrib import admin
from .models import Tenant
from .services import provision_tenant_pipeline
from .migration_service import MigrationService

logger = logging.getLogger(__name__)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        "company_name",
        "db_alias",
        "db_name",
        "db_host",
        "db_port",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["company_name", "db_alias", "db_name"]
    readonly_fields = ["created_at"]
    actions = ["provision_and_migrate_database", "run_tenant_migrations"]

    fieldsets = (
        (
            "Tenant Information",
            {
                "fields": ("company_name", "db_alias", "is_active", "created_at"),
            },
        ),
        (
            "Database Connectivity",
            {
                "fields": ("db_name", "db_user", "db_password", "db_host", "db_port"),
                "description": "Database credentials are automatically encrypted when stored.",
            },
        ),
    )

    @admin.action(description="Provision database & run initial migrations")
    def provision_and_migrate_database(self, request, queryset):
        success_count = 0
        failed_count = 0

        for tenant in queryset:
            try:
                provision_tenant_pipeline(tenant, run_migrations=True)
                success_count += 1
            except Exception as exc:
                failed_count += 1
                logger.exception("Provisioning failed for tenant %s: %s", tenant.db_alias, exc)
                self.message_user(
                    request,
                    f"Error provisioning {tenant.db_alias}: {exc}",
                    level=admin.messages.ERROR,
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully provisioned and migrated {success_count} tenant database(s).",
                level=admin.messages.SUCCESS,
            )

    @admin.action(description="Run pending migrations on selected tenants")
    def run_tenant_migrations(self, request, queryset):
        migrated = 0
        for tenant in queryset.filter(is_active=True):
            try:
                MigrationService.migrate_tenant(tenant)
                migrated += 1
            except Exception as exc:
                self.message_user(
                    request,
                    f"Migration failed for {tenant.db_alias}: {exc}",
                    level=admin.messages.ERROR,
                )
        self.message_user(
            request,
            f"Executed migrations across {migrated} active tenant database(s).",
            level=admin.messages.SUCCESS,
        )
