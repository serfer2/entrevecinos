## Context

TK-002 dejó `DATABASE_URL` sin usar. Ver TK-005 §3 para el detalle de columnas y convenciones.

## Goals / Non-Goals

**Goals:** tabla `users` creada por migración reversible, sesión por petición lista para TK-006, pruebas aisladas de la base de datos de desarrollo.

**Non-Goals:** dominio, repositorios, endpoints, resto de tablas, FK de `avatar_asset_id`.

## Decisions

- **SQLAlchemy 2.0 síncrono + psycopg 3:** endpoints `def` en *threadpool*; pruebas con `TestClient` sin bucles de eventos.
- **Tabla `users`:** evita la palabra reservada `user`; el modelo ORM sigue llamándose `UserModel`.
- **`user_role` como `sqlalchemy.Enum` de cadenas en infraestructura:** el enum de dominio llegará en TK-006 sin acoplar el modelo ORM a él.
- **Alembic recibe la conexión por `config.attributes["connection"]`:** las fixtures migran la base de datos de pruebas sin escribir la URL en `alembic.ini` (evita problemas de interpolación de `%` en `configparser`); si no hay conexión, `env.py` usa `Settings.database_url`.
- **Aislamiento por prueba:** conexión con transacción externa y `Session(join_transaction_mode="create_savepoint")`; los `commit()` del código bajo prueba solo liberan *savepoints* y todo se revierte al final.
- **Base de datos de pruebas:** la fixture deriva `<db>_test` de `DATABASE_URL` y la crea con `CREATE DATABASE` (conexión `AUTOCOMMIT` a la base de datos de desarrollo) si no existe.
- **`make dev` migra con `exec`:** los contenedores ya están en marcha; `make migrate` usa `run --rm` para funcionar aunque `api` esté parado.

## Risks / Trade-offs

- [Las pruebas de `tests/` se copian en la imagen] → tras cambiarlas hay que reconstruir (`make build-backend`), igual que en TK-002.
- [El usuario de PostgreSQL necesita permiso `CREATEDB`] → el usuario creado por la imagen oficial es superusuario en desarrollo.
