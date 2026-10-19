## Why

TK-001, TK-002 y TK-003 definen `db`, `api` y `web` en `infra/docker-compose.yml`, pero cada operación exige escribir `docker compose --env-file .env -f infra/docker-compose.yml ...` con flags distintos, lo que es propenso a errores y frena el onboarding. Ticket de origen: `docs/product/tickets/00-infra/TK-004-makefile-dev-automation.md`.

## What Changes

- Nuevo `Makefile` en la raíz con los targets `help` (por defecto), `build-frontend`, `build-backend`, `build`, `dev` y `clean`, que envuelven Docker Compose sin lógica de infraestructura nueva.
- Comprobación de que existe `$(ENV_FILE)` antes de cualquier comando de Compose.
- Documentación de los comandos en `infra/README.md`.

## Capabilities

### New Capabilities
- `dev-automation`: comandos `make` para construir las imágenes, levantar el entorno de desarrollo completo y limpiarlo sin perder datos.

### Modified Capabilities

## Impact

- Fichero nuevo `Makefile`; cambio en `infra/README.md`.
- Requiere GNU Make y bash. No modifica Compose ni los Dockerfile.
