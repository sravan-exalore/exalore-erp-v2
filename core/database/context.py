import contextvars
from contextlib import contextmanager
from core.tenancy.loader import ensure_tenant_loaded

_current_db = contextvars.ContextVar("tenant_database", default=None)


def get_current_database() -> str | None:
    """Return the active tenant database alias for the current execution context."""
    return _current_db.get()


def set_current_database(db: str | None):
    """Set the active tenant database alias. Returns a contextvar Token."""
    return _current_db.set(db)


def reset_current_database(token) -> None:
    """Reset the tenant context back to the previous state using the provided Token."""
    if token is not None:
        try:
            _current_db.reset(token)
        except Exception:
            _current_db.set(None)


def clear_current_database() -> None:
    """Explicitly reset the context variable to None."""
    _current_db.set(None)


@contextmanager
def tenant_context(db_alias: str):
    """
    Context manager that verifies tenant availability, sets tenant routing context,
    and unconditionally restores the previous context upon exit.
    """
    if not db_alias:
        yield
        return

    if db_alias != "default":
        if not ensure_tenant_loaded(db_alias):
            raise RuntimeError(f"Tenant database '{db_alias}' is unavailable or does not exist.")

    token = set_current_database(db_alias)
    try:
        yield
    finally:
        reset_current_database(token)
