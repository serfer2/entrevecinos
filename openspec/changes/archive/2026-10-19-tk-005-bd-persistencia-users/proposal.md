## Why

HU-01 es la primera historia que guarda datos y el backend todavía no tiene ORM, driver ni migraciones. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-01-registrarme-con-mi-correo-electronico/TK-005-bd-persistencia-y-tabla-users.md`.

## What Changes

- Dependencias `sqlalchemy`, `psycopg[binary]` y `alembic` en `apps/api`.
- `infrastructure/db/` con `Base` (convención de nombres), motor, sesiones y `get_session()`.
- Modelo `UserModel` (tabla `users`) y migración `0001_create_users` con el enum `user_role`.
- Alembic en la imagen y montado en desarrollo; `DATABASE_URL` con esquema `postgresql+psycopg://`.
- `make migrate`; `make dev` aplica las migraciones.
- Fixtures de pruebas con base de datos `<db>_test` y transacción por prueba.

## Capabilities

### New Capabilities
- `user-persistence`: persistencia de usuarios en PostgreSQL (tabla `users`, restricciones, migraciones reversibles y base de datos de pruebas aislada).

### Modified Capabilities

## Impact

- `apps/api` (dependencias, `infrastructure/db`, `migrations/`, `tests/`, `Dockerfile`), `infra/docker-compose.yml`, `Makefile`, `apps/api/README.md`.
