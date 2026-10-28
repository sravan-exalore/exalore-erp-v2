import psycopg2
from django.conf import settings


def create_tenant_database(tenant):
    connection = psycopg2.connect(
        database=settings.DATABASES["default"]["NAME"],
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
        port=settings.DATABASES["default"]["PORT"],
    )

    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute("""SELECT 1 FROM pg_database WHERE datname=%s""", [tenant.db_name])
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f"""CREATE DATABASE "{tenant.db_name}" """)

    cursor.close()
    connection.close()

    tenant.is_active = True
    tenant.save(update_fields=["is_active"])
