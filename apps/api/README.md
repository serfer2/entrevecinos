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

## Configuración

| Variable | Uso | Valor por defecto |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | obligatoria |
| `ASSETS_DIR` | Directorio de ficheros persistentes (volumen `api_assets`) | `/var/lib/entrevecinos/assets` |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas | `http://localhost:3000` |
| `ENVIRONMENT` | `development` o `production` | `development` |

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
