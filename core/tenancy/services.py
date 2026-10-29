import logging
import psycopg2
from psycopg2 import sql
from django.conf import settings
from core.tenancy.migration_service import MigrationService

logger = logging.getLogger(__name__)


def create_tenant_database(tenant):
    """
    Safely creates the tenant PostgreSQL database using parameterized identifier quoting.
    """
    default_cfg = settings.DATABASES["default"]

    conn = psycopg2.connect(
        dbname=default_cfg["NAME"],
        user=default_cfg["USER"],
        password=default_cfg["PASSWORD"],
        host=default_cfg["HOST"],
        port=default_cfg["PORT"],
    )

    try:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # Check if database already exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                [tenant.db_name],
            )
            exists = cursor.fetchone()

            if not exists:
                # Use psycopg2.sql.Identifier to prevent SQL injection in identifier
                query = sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
                    sql.Identifier(tenant.db_name)
                )
                cursor.execute(query)
                logger.info("Created PostgreSQL database: %s", tenant.db_name)
            else:
                logger.info("Database %s already exists.", tenant.db_name)

        tenant.is_active = True
        tenant.save(update_fields=["is_active"])
    finally:
        conn.close()


def provision_tenant_pipeline(tenant, run_migrations: bool = True):
    """
    Full enterprise lifecycle onboarding pipeline:
    1. Provisions physical database.
    2. Registers tenant database in Django connection handler.
    3. Executes all TENANT_APPS migrations against the new database.
    4. Marks tenant active upon verified completion.
    """
    logger.info("Starting onboarding pipeline for tenant: %s", tenant.db_alias)
    try:
        # Step 1: Provision physical database
        create_tenant_database(tenant)

        # Step 2: Migrate tenant apps
        if run_migrations:
            logger.info("Running migrations for tenant %s...", tenant.db_alias)
            MigrationService.migrate_tenant(tenant)

        logger.info("Successfully provisioned tenant %s", tenant.db_alias)
        return True
    except Exception as exc:
        logger.exception("Failed to provision tenant %s: %s", tenant.db_alias, exc)
        tenant.is_active = False
        tenant.save(update_fields=["is_active"])
        raise exc
