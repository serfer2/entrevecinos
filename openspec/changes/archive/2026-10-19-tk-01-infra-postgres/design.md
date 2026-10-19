## Context

Repositorio solo con documentación. Este cambio crea la primera pieza de infraestructura local, sobre la que TK-002 (`api`) y TK-003 (`web`) añadirán servicios en el mismo fichero de Compose. Restricciones del README: PostgreSQL 16, volumen persistente, red interna, sin secretos en el repositorio.

## Goals / Non-Goals

**Goals:**
- Levantar `db` sano con un único comando de Compose.
- Datos persistentes entre `down`/`up`.
- Fallo explícito si falta `POSTGRES_PASSWORD`.
- Base de datos no accesible desde el host por defecto.

**Non-Goals:**
- Esquema, migraciones o datos semilla.
- Servicios `api` y `web`.
- Copias de seguridad y configuración de producción.

## Decisions

- **`postgres:16` (Debian) frente a Alpine:** glibc evita diferencias de *collation* y de búsqueda de texto completo respecto a producción. Solo se fija la versión mayor en local.
- **Volumen con nombre `db_data` frente a *bind mount*:** evita problemas de permisos y que los datos acaben dentro del repositorio.
- **`${POSTGRES_PASSWORD:?...}`:** Compose falla al interpolar si la variable falta, antes de crear nada.
- **Red `data` con `internal: true`:** sin salida ni publicación de puertos; `api` se unirá a ella más adelante. `edge` se declara ya para no reescribir el fichero en TK-002/TK-003.
- **Override `docker-compose.db-debug.yml` frente a puerto siempre publicado:** el acceso desde el host es opcional y limitado a `127.0.0.1`, y el puerto del host es configurable (`POSTGRES_HOST_PORT`) para evitar conflictos con un PostgreSQL local.
- **`.env` en la raíz, Compose en `infra/`:** se usa `--env-file .env -f infra/docker-compose.yml`; las rutas relativas del Compose se resuelven respecto a `infra/`.

## Risks / Trade-offs

- [Los scripts de `initdb` solo se ejecutan con el volumen vacío] → documentado en `infra/README.md`, con el reset mediante `down -v`.
- [Una red `internal` impide publicar puertos desde ella] → el override de depuración añade `db` a la red `edge`, que sí permite publicar en `127.0.0.1`.
- [`down -v` borra los datos de desarrollo] → advertencia en `infra/README.md`.
