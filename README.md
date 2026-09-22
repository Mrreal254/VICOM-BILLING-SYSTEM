# VICOM Billing System

**Phase 1 — Multi-Tenant ISP Billing Foundation**

VICOM Billing System is a Django REST backend foundation for a multi-tenant ISP billing platform.

## Current Phase 1 capabilities

- Custom email-based users and VICOM roles
- ISP tenant registration and tenant lifecycle states
- JWT authentication
- Tenant-aware dashboard APIs
- Super Admin tenant management
- Reusable role permissions
- PostgreSQL / Render database configuration
- Health and root endpoints
- Automated Django tests and CI

## API endpoints

- `GET /health/` — database-backed health check
- `GET /` — service status
- `POST /api/auth/login/` — obtain JWT access/refresh tokens
- `POST /api/auth/refresh/` — refresh JWT
- `POST /api/tenants/register/` — register an ISP tenant
- `GET /api/tenants/dashboard/` — authenticated tenant context
- `GET /api/tenants/dashboard/super-admin/` — Super Admin dashboard
- `GET /api/tenants/dashboard/isp-admin/` — ISP Admin dashboard
- `GET /api/tenants/admin/` — Super Admin tenant list
- `PATCH /api/tenants/admin/<tenant_id>/status/` — update tenant status

## Local development

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Production

Render uses:

```bash
pip install -r requirements.txt
python manage.py migrate --no-input
gunicorn config.wsgi:application
```

Set `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, and `CORS_ALLOWED_ORIGINS` as environment variables in production.

## Scope

Phase 2 will add customers, packages, subscriptions and the related billing domain. M-Pesa, MikroTik, SMS, automation and other integrations remain separate phases.
