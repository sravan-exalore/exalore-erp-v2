import contextvars

_current_database = contextvars.ContextVar("current_database", default=None)


def get_current_database():
    return _current_database.get()


def set_current_database(database):
    return _current_database.set(database)


def reset_current_database(token):
    _current_database.reset(token)
