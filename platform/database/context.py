import contextvars

_current_database = contextvars.ContextVar("current_database", default=None)


def set_current_database(database):
    return _current_database.set(database)


def get_current_database():
    return _current_database.get()


def reset_database(token):
    _current_database.reset(token)
