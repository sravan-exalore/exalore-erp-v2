import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .context import set_current_database
from core.tenancy.loader import ensure_tenant_loaded

logger = logging.getLogger(__name__)


class TenantJWTAuthentication(JWTAuthentication):
    """
    Validates JWT token and binds the authenticated request to the verified tenant database.
    Performs tenant existence, activation, and authorization checks.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if not result:
            return None

        user, token = result

        # Core superusers/staff without a tenant operate on default database
        if not getattr(user, "tenant_id", None):
            set_current_database("default")
            return (user, token)

        database = token.get("database_name")
        tenant_id = token.get("tenant_id")

        if not database:
            raise AuthenticationFailed("Authentication token missing tenant database context.")

        # Cross-tenant integrity check: Token database claim must match the user's bound tenant
        user_tenant = getattr(user, "tenant", None)
        if not user_tenant or user_tenant.db_alias != database or user_tenant.id != tenant_id:
            logger.warning(
                "Cross-tenant mismatch detected for user %s (token: %s, user: %s)",
                user.username,
                database,
                getattr(user_tenant, "db_alias", None),
            )
            raise AuthenticationFailed("Token tenant mismatch. Access denied.")

        if not user_tenant.is_active:
            raise AuthenticationFailed("Tenant organization is inactive or suspended.")

        # Ensure tenant database connection configuration is loaded and ready
        if not ensure_tenant_loaded(database):
            logger.error("Failed to load database configuration for tenant alias: %s", database)
            raise AuthenticationFailed("Tenant database is currently unavailable.")

        # Set tenant routing context for this execution
        set_current_database(database)

        return (user, token)
