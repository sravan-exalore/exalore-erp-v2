from rest_framework.permissions import BasePermission
from core.database.context import get_current_database


class IsTenantUser(BasePermission):
    """
    Requires the request to be authenticated and routed to the user's assigned tenant.
    Rejects requests from deactivated tenants or mismatched contexts.
    """

    message = "Access denied: Request must originate from an authenticated user of an active tenant."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        # Superusers are permitted across views
        if user.is_superuser:
            return True

        tenant = getattr(user, "tenant", None)
        if not tenant or not tenant.is_active:
            return False

        # Verify active database context aligns with user's assigned tenant database
        active_db = get_current_database()
        if active_db and active_db != tenant.db_alias:
            return False

        return True


class IsTenantAdmin(IsTenantUser):
    """
    Requires the user to be an active tenant user with staff/admin status.
    """

    message = "Access denied: Requires tenant administrator privileges."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user = request.user
        return user.is_staff or user.is_superuser


class IsCoreAdmin(BasePermission):
    """
    Requires the user to be a staff or superuser on the core management portal.
    """

    message = "Access denied: Requires core administrative privileges."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))

