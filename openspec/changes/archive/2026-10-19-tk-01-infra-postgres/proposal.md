## Why

El README define que el entorno local se levanta con Docker Compose y que PostgreSQL 16 corre en un contenedor con volumen persistente, en una red interna y sin exponerse fuera de Docker. El repositorio aún no tiene ninguna configuración de Docker, y TK-02 (API) y TK-03 (web) necesitan esta base para añadir sus servicios. Ticket de origen: `docs/product/tickets/00-infra/TK-01-infra-postgres.md`.

## What Changes

- Nuevo `infra/docker-compose.yml` (proyecto `entrevecinos`) con el servicio `db` (`postgres:16`), el volumen con nombre `db_data` y las redes `data` (interna) y `edge`.
- Nuevo `infra/docker-compose.db-debug.yml` opcional que publica la base de datos solo en `127.0.0.1`.
- Nueva carpeta `infra/postgres/initdb/` (vacía, con `.gitkeep`) montada en `/docker-entrypoint-initdb.d/` en solo lectura.
- Nuevo `.env.example` en la raíz con valores ficticios; `.env` excluido en `.gitignore`.
- Nuevo `infra/README.md` con instrucciones de uso.

## Capabilities

### New Capabilities
- `dev-database`: base de datos PostgreSQL 16 del entorno local de desarrollo: arranque sano, persistencia, credenciales obligatorias por entorno, aislamiento de red y acceso de depuración opcional.

### Modified Capabilities

## Impact

- Ficheros nuevos en `infra/` y en la raíz (`.env.example`); cambio en `.gitignore`.
- Requiere Docker con el plugin Compose v2.
- Sin impacto en código de aplicación (todavía no existe). TK-02 y TK-03 ampliarán `infra/docker-compose.yml`.
