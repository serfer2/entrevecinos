# Infraestructura local

Entorno de desarrollo de EntreVecinos con Docker Compose. Todos los comandos se ejecutan desde la **raíz del repositorio**.

## Requisitos

- Docker con el plugin Compose v2 (`docker compose version`).

## Preparación

```bash
cp .env.example .env   # edita al menos POSTGRES_PASSWORD
```

`.env` está excluido del repositorio. Si falta `POSTGRES_PASSWORD`, Compose falla con un mensaje que pide definirla.

> **`.env` creados antes de la validación del correo (Épica 10):** añade las variables de la sección «Correo (SMTP)» de `.env.example` (`SMTP_*`, `MAIL_FROM`, `WEB_PUBLIC_URL`, `EMAIL_VERIFICATION_TTL_HOURS`, `MAIL_UI_HOST_PORT`). Sin `SMTP_HOST`, `MAIL_FROM` o `WEB_PUBLIC_URL`, Compose y la API se niegan a arrancar. Para comprobarlo:
>
> ```bash
> diff <(grep -o '^[A-Z_]*=' .env.example | sort) <(grep -o '^[A-Z_]*=' .env | sort)
> ```

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
| `make dev` | Construye las imágenes, levanta `db`, `mail`, `api` y `web` en segundo plano, aplica las migraciones y muestra las URLs |
| `make migrate` | Aplica las migraciones pendientes de la base de datos |
| `make clean` | Elimina contenedores e imágenes construidas localmente; **conserva** los volúmenes (`db_data`, `storage_data`…) |

Todos comprueban antes que exista `.env`. Para usar otro fichero: `make dev ENV_FILE=.env.local`. Para borrar también los datos, usa `$COMPOSE down -v` (ver más abajo).

## Servicios

| Servicio | Imagen | Redes | Puertos en el host |
|---|---|---|---|
| `db` | `postgres:16` | `data` (interna) | ninguno por defecto |
| `storage` | `pgsty/minio:RELEASE.2026-08-04T00-00-00Z` | `data`, `edge` | `127.0.0.1:${STORAGE_HOST_PORT:-9000}` (API S3) |
| `storage-init` | la misma que `storage` (un solo uso) | `data` | ninguno |
| `mail` | `axllent/mailpit:v1.31.4` | `data`, `edge` | `127.0.0.1:${MAIL_UI_HOST_PORT:-8025}` (interfaz web) |
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
- El healthcheck llama a `GET /v1/health`, que responde 200 solo si la API llega a la base de datos (503 si no).

Más detalles en `apps/api/README.md`.

## Almacenamiento de imágenes (`storage`)

MinIO, compatible con S3, guarda las imágenes; PostgreSQL solo sus metadatos. Los objetos viven en el volumen `storage_data` y sobreviven a `down` (no a `down -v`).

- `storage-init` se ejecuta antes de `api` (`make dev` lo hace solo) y es idempotente: crea el bucket privado `STORAGE_BUCKET`, el usuario de la API (`STORAGE_ACCESS_KEY` / `STORAGE_SECRET_KEY`) y la política `entrevecinos-api`, que solo permite `GetObject`, `PutObject` y `DeleteObject` sobre ese bucket. Script: `infra/storage/init.sh`.
- Solo se publica la API S3 en `127.0.0.1`, porque el navegador abre las URL prefirmadas que genera la API. Sin firma, el bucket responde `403`.
- Las credenciales de administración (`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`) solo las usa `storage-init`; la API usa las suyas.

```bash
$COMPOSE run --rm storage-init                     # volver a inicializar (idempotente)
$COMPOSE -f infra/docker-compose.storage-debug.yml up -d storage   # consola en http://127.0.0.1:9001
```

Si tu `.env` es anterior a este servicio, añade las variables del bloque «Almacenamiento» de `.env.example`; si faltan, Compose falla con un mensaje que las nombra. El volumen `api_assets` de versiones anteriores ya no se usa: `docker volume rm entrevecinos_api_assets`.

### Imagen, versión y licencia

- MinIO, Inc. dejó de publicar imágenes Docker de la edición comunitaria en octubre de 2025 y archivó el proyecto en 2026: `minio/minio` y `minio/mc` ya no están en Docker Hub. Se usa `pgsty/minio`, compilación comunitaria (proyecto Silo, de Pigsty) de la última versión de MinIO, sin cambios en la API S3 y no afiliada a MinIO, Inc. Incluye `mc` y `curl`.
- Versión fijada: `RELEASE.2026-08-04T00-00-00Z` (nunca `latest`). Para actualizar: cambiar la etiqueta en `storage` y `storage-init`, leer las notas de la versión y repetir la verificación (arranque, `403` anónimo, subida y lectura con las credenciales de la API).
- Licencia GNU AGPLv3. EntreVecinos usa MinIO sin modificar, como servicio independiente al que la API accede por el protocolo S3, así que la AGPL no se extiende a su código.
- Solo para desarrollo local: en producción se usa un servicio S3 gestionado. Si la imagen dejara de mantenerse, se puede compilar MinIO desde el código fuente o cambiar a otro servidor compatible con S3 (p. ej. Garage); la API solo depende del protocolo S3.

## Correo (`mail`)

Mailpit recoge todo el correo que envía la API (por ahora, los enlaces de validación del registro) y lo muestra en su interfaz web: en desarrollo no sale ningún correo real.

- http://localhost:8025 — buzón de desarrollo (puerto `MAIL_UI_HOST_PORT`, solo en `127.0.0.1`).
- La API le envía por SMTP a `mail:1025` (red `data`); `edge` solo sirve para publicar la interfaz.
- Sin volumen: los correos se pierden al recrear el contenedor.
- `api` espera a que `mail` esté sano (`/mailpit readyz`).

```bash
$COMPOSE logs -f mail
$COMPOSE exec api python -c \
  "import smtplib; smtplib.SMTP('mail', 1025).sendmail('a@x.test', ['b@x.test'], 'Subject: prueba\n\nhola')"
```

| Variable | Desarrollo | Uso |
|---|---|---|
| `SMTP_HOST` / `SMTP_PORT` | `mail` / `1025` | Servidor SMTP |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | vacías | Credenciales (opcionales) |
| `SMTP_STARTTLS` | `false` | STARTTLS; en producción es obligatorio `true` |
| `MAIL_FROM` | `EntreVecinos <no-reply@entrevecinos.local>` | Remitente |
| `WEB_PUBLIC_URL` | `http://localhost:3000` | Origen de los enlaces del correo; en producción, `https` |
| `EMAIL_VERIFICATION_TTL_HOURS` | `24` | Caducidad del enlace de validación |
| `MAIL_UI_HOST_PORT` | `8025` | Puerto de la interfaz de Mailpit |

En producción basta con apuntar las variables `SMTP_*` al proveedor de correo; `mail` no se despliega.

## Web (`web`)

```bash
$COMPOSE up -d --build web        # levanta db, api y web
$COMPOSE exec web npm run lint
```

- http://localhost:3000 — página marcador.
- `web` solo está en `edge`: no puede alcanzar `db`.
- `apps/web` se monta en el contenedor; `node_modules` y `.next` viven en los volúmenes `web_node_modules` y `web_next_cache`.

Más detalles en `apps/web/README.md`.
