# API de EntreVecinos

Backend en Python con FastAPI, organizado con arquitectura limpia. Las dependencias se gestionan con [uv](https://docs.astral.sh/uv/) dentro del contenedor, así que no hace falta instalar Python ni uv en el host.

## Estructura

```
src/entrevecinos/
├── domain/          # entidades y reglas de negocio, sin dependencias de framework
├── application/     # casos de uso y puertos; solo depende de domain
├── infrastructure/  # adaptadores (configuración, base de datos, ficheros…)
└── presentation/    # FastAPI: create_app() y routers versionados (v1/)
```

Reglas de dependencias (comprobadas por `tests/test_architecture.py`):

- `domain` no importa frameworks (`fastapi`, `starlette`, `pydantic_settings`, `uvicorn`) ni otras capas.
- `application` solo depende de `domain`.
- `infrastructure` y `presentation` pueden depender de `application` y `domain`.

## Ejecutar

Desde la raíz del repositorio (con `.env` creado a partir de `.env.example`):

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE up -d --build api      # levanta db y api; recarga automática al editar src/
```

- Documentación interactiva: http://localhost:8000/docs
- Especificación de referencia de la API: `docs/api/openapi.yaml`

## Base de datos y migraciones

Persistencia con SQLAlchemy 2 (síncrono) y psycopg 3; esquema versionado con Alembic en `migrations/`.

- Modelos ORM: `src/entrevecinos/infrastructure/db/models/` (registrarlos en `models/__init__.py`).
- Sesión por petición: dependencia `get_session()` de `infrastructure/db/session.py` (commit al terminar, rollback si hay error).
- La tabla de usuarios se llama `users` (`user` es palabra reservada en PostgreSQL).

```bash
make migrate                                                  # aplica las migraciones pendientes
$COMPOSE run --rm api alembic current                         # versión actual
$COMPOSE run --rm -v "$PWD/apps/api/migrations:/app/migrations" api \
  alembic revision --autogenerate -m "descripcion"            # nueva migración (revísala siempre)
$COMPOSE run --rm api alembic downgrade -1                    # revertir la última
$COMPOSE run --rm api alembic check                           # el modelo y las migraciones coinciden
```

`make dev` aplica las migraciones al levantar el entorno. Cada migración debe incluir `downgrade()`.

### Pruebas con base de datos

Las pruebas marcadas con `@pytest.mark.db` usan la base de datos `<POSTGRES_DB>_test`, que la fixture `db_engine` crea y migra automáticamente. Cada prueba recibe `db_session`, dentro de una transacción que se revierte al terminar: la base de datos de desarrollo nunca se modifica.

```bash
$COMPOSE run --rm api pytest -m db        # solo integración
$COMPOSE run --rm api pytest -m "not db"  # sin base de datos
```

Las pruebas se copian en la imagen: tras cambiarlas, `make build-backend`.

## Configuración

| Variable | Uso | Valor por defecto |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL (`postgresql+psycopg://…`) | obligatoria |
| `ASSETS_DIR` | Directorio de ficheros persistentes (volumen `api_assets`) | `/var/lib/entrevecinos/assets` |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas | `http://localhost:3000` |
| `ENVIRONMENT` | `development` o `production` | `development` |
| `JWT_SECRET` | Clave de firma de los JWT (HS256, mínimo 32 caracteres) | obligatoria |
| `JWT_TTL_SECONDS` | Duración del token de acceso en segundos | `86400` |

## Autenticación

- `POST /v1/auth/register` crea la cuenta y devuelve un JWT (`AuthResponse`).
- Contraseñas con Argon2id (`pwdlib`); tokens HS256 (`pyjwt`) con `sub`, `iat` y `exp`. El algoritmo está fijado en código.
- Los errores `422` solo devuelven `loc`, `msg` y `type` (nunca los valores enviados).
- Los errores de dominio se traducen a HTTP en `presentation/errors.py`.

## Pruebas y lint

```bash
$COMPOSE run --rm api pytest
$COMPOSE run --rm api ruff check .
$COMPOSE run --rm api ruff format --check .
```

## Dependencias

Se usa la imagen oficial de uv para modificar `pyproject.toml` y `uv.lock` sin instalar nada en el host (desde `apps/api/`):

```bash
UV="docker run --rm -u $(id -u):$(id -g) -e UV_CACHE_DIR=/tmp/uv-cache -v $PWD:/app -w /app --entrypoint uv ghcr.io/astral-sh/uv:0.13.1-python3.12-trixie-slim"
$UV add <paquete>          # runtime
$UV add --dev <paquete>    # desarrollo
$UV lock                   # regenerar el lock
```

Después, reconstruye la imagen (`$COMPOSE build api`). `pyproject.toml` y `uv.lock` se versionan.

## Añadir un módulo funcional

Cada área (usuarios, comunidades, anuncios…) crea su subpaquete en cada capa que necesite:

```
domain/listings/            # entidades y errores de dominio
application/listings/       # casos de uso y puertos (interfaces de repositorio)
infrastructure/listings/    # implementaciones de los puertos
presentation/v1/listings.py # router FastAPI, incluido desde presentation/v1/router.py
```

## Imagen de producción

```bash
docker build --target prod -t entrevecinos-api:prod apps/api
```

Solo instala dependencias de runtime, sin `--reload` y con usuario no root.
