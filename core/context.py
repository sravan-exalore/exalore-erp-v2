"""
Backward-compatible proxy for tenant context management.
Canonical implementation lives in core.database.context.
"""
from core.database.context import (
    get_current_database,
    set_current_database,
    reset_current_database,
    tenant_context,
)

__all__ = [
    "get_current_database",
    "set_current_database",
    "reset_current_database",
    "tenant_context",
]
