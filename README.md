# Exalore Backend

Django REST backend with PostgreSQL-backed tenant databases. The default
database stores authentication and tenant records; tenant-specific application
models are routed to each tenant database.

## Requirements

- Python 3.14
- PostgreSQL

Install the Python dependencies:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configure the default PostgreSQL connection using these environment variables.
If omitted, the development defaults in `config/settings.py` are used.

```powershell
$env:POSTGRES_DB = "exalore_default"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "root"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
```

Apply default-database migrations and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

The login endpoint is `POST /user/login/`.

## Project layout

- `config/` — Django settings and ASGI, WSGI, and URL configuration.
- `core/authentication/` — Default-database user model and admin integration.
- `core/tenancy/` — Tenant model, provisioning, registration, and migration
  services.
- `core/database/` — Database routing, tenant context, and JWT authentication.
- `core/management/commands/` — Commands for migrating default and tenant
  databases.
- `apps/` — Application models and authentication endpoints.

## Tenant database migrations

After creating and provisioning a tenant, use its database alias to migrate it:

```powershell
python manage.py migrate_tenant <tenant-db-alias>
```

To migrate all active tenant databases:

```powershell
python manage.py migrate_all_tenants
```

Tenant application labels are configured in `TENANT_APPS`; core authentication
and tenancy labels are configured in `DEFAULT_APPS`.
