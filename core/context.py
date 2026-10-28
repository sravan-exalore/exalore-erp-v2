from contextlib import contextmanager
from core.database.context import set_current_database, reset_current_database


@contextmanager
def tenant_context(database):
    token = set_current_database(database)

    try:
        yield

    finally:
        reset_current_database(token)
