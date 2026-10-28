from django.conf import settings


def register_tenant_database(tenant):
    alias = tenant.db_alias

    if alias in settings.DATABASES:
        return alias

    settings.DATABASES[alias] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": tenant.db_name,
        "USER": tenant.db_user,
        "PASSWORD": tenant.get_password(),
        "HOST": tenant.db_host,
        "PORT": tenant.db_port,
        "CONN_MAX_AGE": 60,
    }

    return alias
