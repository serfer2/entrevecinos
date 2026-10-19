# TK-005 · Base de datos: capa de persistencia y tabla `users`

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos / backend |
| **Componente** | `apps/api/` (`infrastructure/db/`, `migrations/`), `infra/`, `Makefile` |
| **Historia** | HU-01 Registrarme con mi correo electrónico (Épica 1) |
| **Prioridad** | Alta (bloquea TK-006 y todos los tickets que guardan datos) |
| **Depende de** | TK-001, TK-002, TK-004 |
| **Referencias** | `readme.md` §3.1 y §3.2 (entidad `user`, enum `user_role`), §2.3 (arquitectura limpia); `docs/api/components/schemas/User.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-002 dejó el backend sin ORM, driver ni migraciones (`DATABASE_URL` se define pero no se usa). HU-01 es la primera historia que guarda datos, así que necesita la capa de persistencia y la tabla de usuarios.

**Objetivo:** añadir SQLAlchemy, el driver de PostgreSQL y Alembic al backend; crear la primera migración con el enum `user_role` y la tabla `users`, que implementa la entidad `user` del modelo de datos; y automatizar la aplicación de migraciones en el entorno de desarrollo. **No se implementa ningún endpoint.**

## 2. Alcance

**Incluye**
- Dependencias `sqlalchemy`, `psycopg` y `alembic`.
- Motor, fábrica de sesiones y `Base` declarativa en `infrastructure/db/`.
- Modelo ORM `UserModel` y primera migración (`user_role` + `users`).
- Configuración de Alembic (`alembic.ini`, `migrations/`), incluida en la imagen y montada en desarrollo.
- Target `make migrate`, y `make dev` aplica las migraciones al levantar el entorno.
- Base de datos de pruebas creada automáticamente por las fixtures de `pytest`.
- Ampliación de `test_architecture.py` con las nuevas librerías de infraestructura.

**No incluye**
- Entidades de dominio, casos de uso, repositorios ni endpoints (TK-006).
- Resto de tablas del modelo (`community`, `listing`, `media_asset`…), que se crean en los tickets de cada historia.
- Clave foránea `users.avatar_asset_id → media_asset.id`: la columna se crea, pero la FK se añade cuando exista `media_asset` (asumido).

## 3. Requisitos técnicos

### 3.1 Dependencias (`apps/api/pyproject.toml`)

- Runtime: `sqlalchemy>=2.0`, `psycopg[binary]>=3.2`, `alembic>=1.14`.
- Regenerar `uv.lock` con la imagen de uv (ver `apps/api/README.md`).

**Decisión (asumido): SQLAlchemy 2.0 síncrono con psycopg 3.** FastAPI ejecuta los endpoints `def` en un *threadpool*, lo que basta para el MVP. Además, las pruebas con `TestClient` son más sencillas que con sesiones asíncronas. Si más adelante se necesita `async`, psycopg 3 lo admite sin cambiar de driver.

### 3.2 Cadena de conexión

- `infra/docker-compose.yml`: `DATABASE_URL` pasa a `postgresql+psycopg://...@db:5432/...` (el riesgo ya estaba previsto en TK-002 §8).
- `Settings.database_url` no cambia de tipo.

### 3.3 Estructura de ficheros

```
apps/api/
├── alembic.ini
├── migrations/
│   ├── env.py                    # lee DATABASE_URL de Settings y usa Base.metadata
│   ├── script.py.mako
│   └── versions/
│       └── 0001_create_users.py
└── src/entrevecinos/infrastructure/db/
    ├── __init__.py
    ├── base.py                   # DeclarativeBase con convención de nombres
    ├── session.py                # create_engine(), sessionmaker, get_session()
    └── models/
        ├── __init__.py           # importa todos los modelos (para autogenerate)
        └── user.py               # UserModel (__tablename__ = "users")
```

### 3.4 Convenciones de la base de datos

- `Base.metadata` con `naming_convention` explícita (`pk_%(table_name)s`, `uq_%(table_name)s_%(column_0_name)s`, `ix_…`, `fk_…`, `ck_…`) para que las migraciones generen nombres estables.
- Fechas en `TIMESTAMPTZ` (`DateTime(timezone=True)`), siempre en UTC.
- Identificadores `UUID` con `server_default=text("gen_random_uuid()")` (incluido en PostgreSQL ≥ 13).
- Las migraciones se escriben a mano o se revisan siempre tras `--autogenerate`; cada una incluye `downgrade()`.

### 3.5 Tabla `users` (migración `0001_create_users`)

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `UUID` | PK, `DEFAULT gen_random_uuid()` |
| `email` | `VARCHAR(320)` | `NOT NULL`, `UNIQUE`, `CHECK (email = lower(email))` |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` |
| `full_name` | `VARCHAR(120)` | `NOT NULL`, `CHECK (length(trim(full_name)) > 0)` (asumido) |
| `phone` | `VARCHAR(32)` | `NULL` |
| `avatar_asset_id` | `UUID` | `NULL` (FK pendiente, ver §2) |
| `platform_role` | `user_role` | `NOT NULL`, `DEFAULT 'user'` |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT true` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()`; la aplicación lo actualiza en cada cambio (`onupdate`) (asumido) |
| `deleted_at` | `TIMESTAMPTZ` | `NULL` (borrado lógico) |

- Enum PostgreSQL `user_role` con valores `user` y `platform_admin`.
- **Nombre de la tabla: `users`.** La entidad del modelo de datos se llama `user` (`readme.md` §3), pero `user` es palabra reservada en PostgreSQL y obligaría a entrecomillarla en todo el SQL manual. La entidad de dominio y el modelo ORM se siguen llamando `User` y `UserModel`.
- Las claves foráneas de otras tablas hacia usuarios (`created_by`, `user_id`, `reviewed_by`…) apuntan a `users.id`.

### 3.6 Sesión por petición

`session.py` expone:
- `get_engine()`: motor con caché, creado desde `Settings.database_url` (`pool_pre_ping=True`).
- `SessionLocal`: `sessionmaker(expire_on_commit=False)`.
- `get_session()`: generador para la dependencia de FastAPI. Hace `commit` al terminar, `rollback` si hay excepción, y siempre cierra la sesión. Lo usarán TK-006 y siguientes.

### 3.7 Docker, Compose y Makefile

- `apps/api/Dockerfile`: copiar `alembic.ini` y `migrations/` en las etapas `dev` y `prod`.
- `infra/docker-compose.yml` (servicio `api`): montar también `../apps/api/migrations:/app/migrations` y `../apps/api/alembic.ini:/app/alembic.ini:ro` en desarrollo.
- `Makefile`:
  - `migrate: check-env ## Aplica las migraciones pendientes` → `$(COMPOSE) run --rm api alembic upgrade head`.
  - `dev` aplica las migraciones después de levantar `db` y antes de dar por terminado el arranque.

### 3.8 Pruebas

- `tests/conftest.py`: fixture de sesión que:
  1. Deriva la URL de pruebas de `DATABASE_URL`, cambiando el nombre de la base de datos a `<db>_test` (asumido).
  2. Crea esa base de datos si no existe, conectándose con el mismo usuario.
  3. Ejecuta `alembic upgrade head` una vez por sesión de `pytest`.
  4. Envuelve cada prueba en una transacción que se revierte al terminar, para aislarlas entre sí.
- Las pruebas de integración se marcan con `@pytest.mark.db`. Las pruebas existentes (arranque y arquitectura) no necesitan base de datos.
- `test_architecture.py`: añadir `sqlalchemy`, `alembic` y `psycopg` a las librerías prohibidas en `domain` y `application`.

## 4. Criterios de aceptación

**AC1 — Migración aplicada**

- **Given** el entorno levantado con `make dev`
- **When** consulto `\d users` en `psql`
- **Then** existe la tabla `users` con las columnas, tipos, valores por defecto y restricciones de §3.5, y el enum `user_role` con `user` y `platform_admin`

**AC2 — Migración reversible**

- **Given** la base de datos en la última versión
- **When** ejecuto `alembic downgrade base` y después `alembic upgrade head`
- **Then** ambos comandos terminan sin errores y la tabla vuelve a existir

**AC3 — Unicidad y normalización del correo**

- **Given** un usuario con el correo `vecino@example.com`
- **When** intento insertar otro con `vecino@example.com`, o uno con `Vecino@Example.com`
- **Then** la base de datos rechaza el primero por la restricción `UNIQUE` y el segundo por la restricción `CHECK` de minúsculas

**AC4 — Valores por defecto**

- **Given** una inserción con solo `email`, `password_hash` y `full_name`
- **When** leo la fila insertada
- **Then** tiene `id` generado, `platform_role = 'user'`, `is_active = true`, `created_at` y `updated_at` en UTC, y `phone`, `avatar_asset_id` y `deleted_at` nulos

**AC5 — Pruebas aisladas**

- **Given** la base de datos de desarrollo con datos
- **When** ejecuto `pytest`
- **Then** las pruebas usan `<db>_test`, no modifican la base de datos de desarrollo y pasan, igual que `ruff check`

## 5. Plan de tareas

1. Añadir dependencias y regenerar `uv.lock`.
2. Implementar `base.py` (convención de nombres) y `session.py`.
3. Implementar `UserModel`.
4. Inicializar Alembic, adaptar `env.py` a `Settings` y `Base.metadata`, y escribir `0001_create_user`.
5. Actualizar `Dockerfile`, Compose (`DATABASE_URL`, montajes) y `Makefile` (`migrate`, `dev`).
6. Escribir las fixtures de base de datos de pruebas y las pruebas de AC3 y AC4.
7. Ampliar `test_architecture.py`.
8. Documentar migraciones en `apps/api/README.md` (crear, aplicar, revertir) y verificar según la sección 6.

## 6. Verificación

```bash
make dev                                                    # levanta y migra
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec db psql -U entrevecinos -c '\d users'           # AC1
$COMPOSE exec db psql -U entrevecinos -c '\dT+ user_role'
$COMPOSE run --rm api alembic downgrade base                # AC2
$COMPOSE run --rm api alembic upgrade head
$COMPOSE run --rm api alembic current                       # 0001 (head)
$COMPOSE run --rm api pytest                                # AC3–AC5
$COMPOSE run --rm api ruff check .
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan en el contenedor.
- [ ] `make migrate` es idempotente y `make dev` deja la base de datos migrada.
- [ ] `domain` y `application` siguen sin importar SQLAlchemy (lo comprueba la prueba de arquitectura).
- [ ] `apps/api/README.md` documenta el flujo de migraciones.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Nombre de tabla distinto del de la entidad:** la tabla se llama `users` y la entidad del modelo de datos `user` (ver §3.5). Conviene reflejarlo en `readme.md` §3 para que el diagrama y la base de datos coincidan.
- **Síncrono frente a asíncrono:** ver §3.1. Cambiarlo más adelante afecta a repositorios y fixtures, no al dominio.
- **FK de `avatar_asset_id`:** pendiente hasta que exista `media_asset`.
- **Migraciones en producción:** aquí se aplican con `make`; en cloud se ejecutarán como paso previo del despliegue (entrega 3).
