import logging
from core.tenancy.models import Tenant
from core.tenancy.services import provision_tenant_pipeline
from core.tenancy.migration_service import MigrationService

logger = logging.getLogger(__name__)

# Fallback decorator if celery is not installed yet
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func):
            def wrapper(*a, **kw):
                return func(*a, **kw)
            wrapper.delay = func
            return wrapper
        return decorator


@shared_task(bind=True, max_retries=3)
def provision_tenant_async(self, tenant_id: int):
    """
    Asynchronously provision a tenant database and execute migrations.
    """
    try:
        tenant = Tenant.objects.using("default").get(id=tenant_id)
        logger.info("Executing async provisioning for tenant: %s", tenant.db_alias)
        provision_tenant_pipeline(tenant, run_migrations=True)
        return {"status": "success", "tenant": tenant.db_alias}
    except Exception as exc:
        logger.exception("Async provisioning failed for tenant ID %s: %s", tenant_id, exc)
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True, max_retries=2)
def migrate_tenant_async(self, tenant_id: int):
    """
    Asynchronously executes pending migrations on a specific tenant database.
    """
    try:
        tenant = Tenant.objects.using("default").get(id=tenant_id)
        logger.info("Executing async migration for tenant: %s", tenant.db_alias)
        MigrationService.migrate_tenant(tenant)
        return {"status": "success", "tenant": tenant.db_alias}
    except Exception as exc:
        logger.exception("Async migration failed for tenant ID %s: %s", tenant_id, exc)
        raise self.retry(exc=exc, countdown=15)

