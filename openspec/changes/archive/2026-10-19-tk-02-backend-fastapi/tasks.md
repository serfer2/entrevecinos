## 1. Proyecto Python

- [x] 1.1 Crear `apps/api/pyproject.toml` (Python ≥3.12, dependencias runtime y grupo `dev`, configuración de ruff y pytest)
- [x] 1.2 Crear el paquete `entrevecinos` con `domain`, `application`, `infrastructure` y `presentation/v1`
- [x] 1.3 Generar `uv.lock` con la imagen de uv

## 2. Aplicación

- [x] 2.1 Implementar `infrastructure/settings.py` (`Settings`, `get_settings()`, `cors_origins_list`)
- [x] 2.2 Implementar `presentation/v1/router.py` (router `/v1` vacío) y `presentation/main.py` (`create_app()` con CORS, `app`)

## 3. Pruebas

- [x] 3.1 `tests/test_app.py`: título, versión, `paths` vacío, `/docs` 200, CORS y fallo sin `DATABASE_URL`
- [x] 3.2 `tests/test_architecture.py`: imports prohibidos en `domain` y `application`

## 4. Docker

- [x] 4.1 `apps/api/Dockerfile` con etapas `dev` y `prod`, usuario no root y `ASSETS_DIR`
- [x] 4.2 `apps/api/.dockerignore`
- [x] 4.3 Añadir el servicio `api` y el volumen `api_assets` a `infra/docker-compose.yml`
- [x] 4.4 Añadir `API_PORT` y `CORS_ORIGINS` a `.env.example`

## 5. Documentación

- [x] 5.1 `apps/api/README.md` (ejecutar, probar, añadir un módulo por capas) y actualizar `infra/README.md`

## 6. Verificación

- [x] 6.1 `pytest` y `ruff check` pasan en el contenedor
- [x] 6.2 `api` healthy, `/openapi.json` con `paths` vacío, usuario no root
- [x] 6.3 Fichero en `ASSETS_DIR` persiste tras `--force-recreate`
- [x] 6.4 La imagen `prod` se construye y arranca
