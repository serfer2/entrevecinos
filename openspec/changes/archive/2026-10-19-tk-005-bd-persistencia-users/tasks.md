## 1. Dependencias y base

- [x] 1.1 Añadir `sqlalchemy`, `psycopg[binary]` y `alembic`; regenerar `uv.lock`
- [x] 1.2 `infrastructure/db/base.py` (convención de nombres) y `session.py` (`get_engine`, `SessionLocal`, `get_session`)
- [x] 1.3 `infrastructure/db/models/user.py` (`UserModel`, tabla `users`)

## 2. Migraciones

- [x] 2.1 `alembic.ini`, `migrations/env.py`, `script.py.mako`
- [x] 2.2 `migrations/versions/0001_create_users.py` con `upgrade` y `downgrade`

## 3. Entorno

- [x] 3.1 `Dockerfile` copia `alembic.ini` y `migrations/`
- [x] 3.2 Compose: `DATABASE_URL` `postgresql+psycopg://` y montajes de migraciones
- [x] 3.3 `Makefile`: `migrate`; `dev` aplica las migraciones

## 4. Pruebas

- [x] 4.1 Fixtures de base de datos de pruebas en `tests/conftest.py` y marcador `db`
- [x] 4.2 Pruebas de restricciones y valores por defecto (AC3, AC4) y de migración reversible (AC2)
- [x] 4.3 Ampliar `test_architecture.py` con `sqlalchemy`, `alembic` y `psycopg`

## 5. Documentación y verificación

- [x] 5.1 Flujo de migraciones en `apps/api/README.md`
- [x] 5.2 Verificación TK-005 §6
