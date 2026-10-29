from .context import (
    set_current_database,
    reset_current_database,
    clear_current_database,
)
from core.tenancy.loader import ensure_tenant_loaded


class TenantMiddleware:
    """
    Guarantees tenant isolation per request lifecycle.
    Ensures that context variables are unconditionally cleared when the HTTP response cycle ends,
    preventing any context leakage across thread pools or async workers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        database = None

        # 1. Resolve from authenticated session (Admin / SSR views)
        if hasattr(request, "session"):
            database = request.session.get("selected_database")

        # 2. Resolve from optional header (internal microservices / webhooks)
        if not database:
            header_alias = request.headers.get("X-Tenant-Alias")
            if header_alias and ensure_tenant_loaded(header_alias):
                database = header_alias

        # Capture token at entrance (could be setting None or the session/header db)
        entry_token = set_current_database(database)

        try:
            response = self.get_response(request)
        finally:
            # Unconditionally restore previous context and guarantee no leakage
            reset_current_database(entry_token)
            clear_current_database()

        return response
