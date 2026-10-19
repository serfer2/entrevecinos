## Context

TK-001 dejó `infra/docker-compose.yml` con `db` en la red interna `data` y la red `edge` declarada. Este cambio añade el backend vacío. `uv` no está instalado en el host, así que todo el flujo Python (lock, pruebas, lint) se ejecuta en contenedores.

## Goals / Non-Goals

**Goals:**
- `api` arranca `healthy` en Compose y expone `/docs` con `paths` vacío.
- Las reglas de la arquitectura limpia se comprueban con una prueba automática.
- La configuración falla de forma explícita si falta `DATABASE_URL`.
- Contenedor no root con volumen de assets escribible y persistente.

**Non-Goals:**
- Endpoints, `/health`, ORM, driver de PostgreSQL, migraciones, JWT/RBAC, cliente S3.

## Decisions

- **uv como gestor, copiado desde `ghcr.io/astral-sh/uv:0.13.1`:** instalaciones reproducibles con `uv.lock` sin instalar nada en el host. Alternativa (pip + requirements) descartada: sin lock de calidad equivalente.
- **Entorno virtual en `/opt/venv`, fuera de `/app`:** el montaje de `../apps/api/src:/app/src` en desarrollo no pisa las dependencias instaladas.
- **Paquete instalado en modo editable en `dev`:** `uv sync` instala `entrevecinos` apuntando a `/app/src`, así la recarga de uvicorn ve los cambios montados. En `prod` se instala sin modo editable (`--no-editable`) y sin dependencias de desarrollo.
- **`CORS_ORIGINS` como cadena separada por comas:** se expone como lista a través de una propiedad; evita el formato JSON que pydantic-settings exige por defecto para listas.
- **`get_settings()` con caché llamado desde `create_app()`:** un `DATABASE_URL` ausente provoca `ValidationError` al importar la app, y el proceso termina.
- **Prueba de arquitectura con `ast`:** recorre los `.py` de `domain` y `application` y comprueba sus `import`; no ejecuta el código, así detecta imports aunque estén en ramas no ejecutadas.
- **Healthcheck por TCP:** no existe endpoint de salud; se sustituirá cuando se implemente `/health`.
- **`tests/` en la imagen `dev`, excluidos de `prod`:** `docker compose run --rm api pytest` funciona sin montar `tests/`.

## Risks / Trade-offs

- [Permisos del volumen `api_assets`] → el directorio se crea en la imagen con el usuario no root como propietario; Docker copia esos permisos al inicializar el volumen vacío.
- [El esquema de `DATABASE_URL` puede cambiar con el driver] → se ajustará en el ticket de persistencia.
- [Volumen local frente a MinIO] → decisión abierta del ticket; el acceso a ficheros quedará detrás de un puerto de `application`.
