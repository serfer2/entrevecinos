## Why

El README define un backend FastAPI en contenedor Docker, organizado con arquitectura limpia (`domain`, `application`, `infrastructure`, `presentation`) en `apps/api/src/entrevecinos/`. No existe todavía ningún código de backend y todas las funcionalidades dependen de esta base. Ticket de origen: `docs/product/tickets/00-infra/TK-02-backend-fastapi.md`.

## What Changes

- Nuevo proyecto Python en `apps/api/` (`pyproject.toml`, `uv.lock`) con FastAPI, uvicorn y pydantic-settings; pytest, httpx2 (cliente de pruebas que recomienda Starlette en lugar de httpx) y ruff para desarrollo.
- Paquete `entrevecinos` con las cuatro capas vacías, `Settings` por entorno, `create_app()` con CORS y un router `/v1` sin rutas.
- Pruebas de arranque y de dependencias entre capas.
- `Dockerfile` con etapas `dev` y `prod`, usuario no root, y `.dockerignore`.
- Servicio `api` y volumen `api_assets` en `infra/docker-compose.yml`; `API_PORT` y `CORS_ORIGINS` en `.env.example`.
- `apps/api/README.md`.

## Capabilities

### New Capabilities
- `api-skeleton`: esqueleto del backend: aplicación FastAPI vacía bajo `/v1`, configuración por entorno, reglas de dependencias entre capas, contenedor no root y volumen persistente de assets.

### Modified Capabilities

## Impact

- Código nuevo en `apps/api/`; cambios en `infra/docker-compose.yml`, `.env.example` e `infra/README.md`.
- Nuevas dependencias: Python 3.12, FastAPI, uvicorn, pydantic-settings, uv (dentro de la imagen).
- No se implementan endpoints de negocio ni `/health`.
