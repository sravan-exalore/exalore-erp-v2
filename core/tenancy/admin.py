from django.contrib import admin
from .models import Tenant
from .services import create_tenant_database


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["company_name", "db_alias", "is_active"]
    actions = ["provision_database"]

    @admin.action(description="Create tenant database")
    def provision_database(self, request, queryset):
        for tenant in queryset:
            create_tenant_database(tenant)

        self.message_user(request, "Tenant database provisioning completed")
