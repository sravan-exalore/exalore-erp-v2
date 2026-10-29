import logging
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.general.models import GnUser
from core.database.context import tenant_context
from core.tenancy.models import Tenant

logger = logging.getLogger(__name__)
User = get_user_model()


def create_tenant_user(tenant_db: str, username: str, password: str, **kwargs):
    """
    Creates a user in the central authentication DB linked to the tenant,
    and initializes their corresponding GnUser ERP profile in the tenant DB.
    Guarantees atomic rollback on failure.
    """
    try:
        tenant = Tenant.objects.using("default").get(db_alias=tenant_db, is_active=True)
    except Tenant.DoesNotExist:
        raise ValueError(f"Active tenant with alias '{tenant_db}' not found.")

    email = kwargs.get("email", "")
    first_name = kwargs.get("first_name", "")
    last_name = kwargs.get("last_name", "")

    # 1. Create central user
    default_user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        tenant=tenant,
    )

    # 2. Create tenant-scoped profile
    try:
        with tenant_context(tenant_db):
            gn_user = GnUser.objects.create(
                default_user_id=default_user.id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        return default_user, gn_user
    except Exception as exc:
        logger.error("Failed to create tenant user in %s; rolling back default user: %s", tenant_db, exc)
        default_user.delete()
        raise exc
