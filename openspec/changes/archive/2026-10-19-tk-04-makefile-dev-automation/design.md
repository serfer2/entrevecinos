## Context

El Compose de `infra/` ya define `db`, `api` y `web`. El Makefile es una capa fina encima.

## Goals / Non-Goals

**Goals:**
- Comandos cortos e idempotentes para construir, levantar y limpiar.
- Un único punto de verdad (`COMPOSE`) para los flags.

**Non-Goals:**
- Targets de producción, test, lint o CI.
- Borrar volúmenes (`down -v`).

## Decisions

- **`check-env` como prerequisito `.PHONY`:** cada target que usa Compose depende de él; falla pronto con un mensaje claro si falta `$(ENV_FILE)`.
- **`build` = prerequisitos `build-frontend build-backend`:** sin repetir comandos.
- **`dev` con `up -d`:** el ticket asume modo *detached*; al terminar muestra las URLs de `web` y `api`.
- **`clean` con `down --rmi local --remove-orphans`:** `--rmi local` elimina solo las imágenes sin etiqueta propia, es decir, las construidas por Compose (`entrevecinos-api`, `entrevecinos-web`), y conserva `postgres:16`. Sin `-v`, se conservan `db_data`, `api_assets` y los volúmenes de caché.
- **Puertos en el mensaje de `dev`:** se leen de `$(ENV_FILE)` con `grep`, con 3000/8000 por defecto.
- **`help` autodocumentado:** `grep` de comentarios `##` en el propio Makefile.

## Risks / Trade-offs

- [`/v1/health` aún no existe] → la verificación de `api` usa `/docs`.
- [El volumen `web_node_modules` sobrevive a `clean`] → tras cambiar dependencias del frontend se recrea según `apps/web/README.md`.
