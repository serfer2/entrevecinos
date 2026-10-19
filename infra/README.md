# Infraestructura local

Entorno de desarrollo de EntreVecinos con Docker Compose. Todos los comandos se ejecutan desde la **raíz del repositorio**.

## Requisitos

- Docker con el plugin Compose v2 (`docker compose version`).

## Preparación

```bash
cp .env.example .env   # edita al menos POSTGRES_PASSWORD
```

`.env` está excluido del repositorio. Si falta `POSTGRES_PASSWORD`, Compose falla con un mensaje que pide definirla.

Para abreviar, en los ejemplos:

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
```

## Comandos rápidos (`make`)

El `Makefile` de la raíz envuelve los comandos de Compose más habituales:

| Comando | Qué hace |
|---|---|
| `make` / `make help` | Lista los comandos disponibles |
| `make build-frontend` | Construye solo la imagen de `web` |
| `make build-backend` | Construye solo la imagen de `api` |
| `make build` | Construye las imágenes de `web` y `api` |
| `make dev` | Construye las imágenes, levanta `db`, `api` y `web` en segundo plano y aplica las migraciones |
| `make migrate` | Aplica las migraciones pendientes de la base de datos |
| `make clean` | Elimina contenedores e imágenes construidas localmente; **conserva** los volúmenes (`db_data`, `api_assets`…) |

Todos comprueban antes que exista `.env`. Para usar otro fichero: `make dev ENV_FILE=.env.local`. Para borrar también los datos, usa `$COMPOSE down -v` (ver más abajo).

## Servicios

| Servicio | Imagen | Redes | Puertos en el host |
|---|---|---|---|
| `db` | `postgres:16` | `data` (interna) | ninguno por defecto |
| `api` | `apps/api/Dockerfile` (etapa `dev`) | `data`, `edge` | `${API_PORT:-8000}` |
| `web` | `apps/web/Dockerfile` (etapa `dev`) | `edge` | `${WEB_PORT:-3000}` |

- `data`: red interna (`internal: true`). La base de datos no es accesible desde fuera de Docker.
- `edge`: red normal para los servicios que deben ser accesibles desde el navegador.

## Base de datos (`db`)

```bash
$COMPOSE up -d db                 # levantar
$COMPOSE ps                       # debe aparecer como healthy
$COMPOSE exec db psql -U entrevecinos -d entrevecinos   # consola SQL
$COMPOSE stop db                  # parar sin borrar nada
$COMPOSE down                     # eliminar contenedores (los datos se conservan)
```

Los datos viven en el volumen con nombre `db_data` y sobreviven a `down`.

### Borrar los datos

```bash
$COMPOSE down -v                  # ⚠️ elimina el volumen db_data y todos los datos
```

### Scripts de inicialización

Los ficheros `*.sql` o `*.sh` de `infra/postgres/initdb/` se montan en `/docker-entrypoint-initdb.d/` y **solo se ejecutan cuando el volumen está vacío** (primer arranque). Si cambias un script, tienes que borrar el volumen (`down -v`) para que vuelva a ejecutarse.

### Conectar un cliente desde el host

Por defecto `db` no publica ningún puerto. Para depurar con un cliente local (psql, DBeaver…), añade el override de depuración:

```bash
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.db-debug.yml up -d db
psql -h 127.0.0.1 -p 5432 -U entrevecinos entrevecinos
```

El puerto se publica solo en `127.0.0.1` y se puede cambiar con `POSTGRES_HOST_PORT` en `.env` si el 5432 ya está ocupado. Vuelve a la configuración por defecto con `$COMPOSE up -d db`.

## API (`api`)

```bash
$COMPOSE up -d --build api        # levanta db (si hace falta) y la API
$COMPOSE run --rm api pytest      # pruebas
$COMPOSE logs -f api              # logs
```

- http://localhost:8000/docs — documentación interactiva.
- `apps/api/src` se monta en el contenedor y uvicorn recarga al guardar.
- Los ficheros de `ASSETS_DIR` viven en el volumen `api_assets` y sobreviven a `down` (no a `down -v`).
- El healthcheck comprueba el puerto TCP hasta que exista el endpoint `/v1/health`.

Más detalles en `apps/api/README.md`.

## Web (`web`)

```bash
$COMPOSE up -d --build web        # levanta db, api y web
$COMPOSE exec web npm run lint
```

- http://localhost:3000 — página marcador.
- `web` solo está en `edge`: no puede alcanzar `db`.
- `apps/web` se monta en el contenedor; `node_modules` y `.next` viven en los volúmenes `web_node_modules` y `web_next_cache`.

Más detalles en `apps/web/README.md`.
