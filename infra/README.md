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

## Servicios

| Servicio | Imagen | Redes | Puertos en el host |
|---|---|---|---|
| `db` | `postgres:16` | `data` (interna) | ninguno por defecto |

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
