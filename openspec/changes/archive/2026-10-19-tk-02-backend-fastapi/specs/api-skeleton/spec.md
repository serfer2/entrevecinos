## ADDED Requirements

### Requirement: Aplicación vacía bajo /v1
El backend SHALL exponer una aplicación FastAPI titulada `API de EntreVecinos`, versión `1.0.0`, con un router `/v1` montado y sin ninguna ruta propia.

#### Scenario: Esquema OpenAPI vacío
- **WHEN** la API está en marcha y se consulta `/openapi.json`
- **THEN** el campo `paths` es un objeto vacío y `/docs` responde 200

### Requirement: Configuración por entorno
La configuración SHALL leerse de variables de entorno (`DATABASE_URL`, `ASSETS_DIR`, `CORS_ORIGINS`, `ENVIRONMENT`) y MUST fallar con un error explícito si `DATABASE_URL` no está definida.

#### Scenario: Falta DATABASE_URL
- **WHEN** la aplicación se crea sin `DATABASE_URL` en el entorno
- **THEN** se lanza un error de validación de configuración que nombra `DATABASE_URL`

### Requirement: CORS restringido
La aplicación SHALL permitir solo los orígenes listados en `CORS_ORIGINS` (por defecto `http://localhost:3000`) y MUST NOT usar `*` por defecto.

#### Scenario: Origen no autorizado
- **WHEN** llega una petición preflight desde un origen que no está en `CORS_ORIGINS`
- **THEN** la respuesta no incluye `Access-Control-Allow-Origin` para ese origen

### Requirement: Dependencias entre capas
`domain` MUST NOT importar librerías de framework (`fastapi`, `pydantic_settings`, `uvicorn`, `starlette`) ni las capas `application`, `infrastructure` o `presentation`; `application` MUST NOT importar esas librerías ni `infrastructure` o `presentation`. Una prueba automática SHALL comprobarlo.

#### Scenario: Import prohibido en domain
- **WHEN** un módulo de `domain` importa `fastapi`
- **THEN** `pytest` falla en la prueba de arquitectura

### Requirement: Contenedor de la API
El servicio `api` de Compose SHALL construirse desde `apps/api/Dockerfile` (etapa `dev`), depender de `db` sano, estar en las redes `data` y `edge`, publicar `${API_PORT:-8000}` y ejecutarse con un usuario distinto de root.

#### Scenario: Arranque en Compose
- **WHEN** se ejecuta `docker compose --env-file .env -f infra/docker-compose.yml up -d --build api`
- **THEN** el contenedor `api` queda `healthy` e `id -u` dentro del contenedor es distinto de 0

### Requirement: Persistencia de assets
El directorio `ASSETS_DIR` (`/var/lib/entrevecinos/assets`) SHALL estar en el volumen con nombre `api_assets`, ser escribible por el usuario no root y sobrevivir a la recreación del contenedor.

#### Scenario: Fichero tras recrear el contenedor
- **WHEN** se escribe un fichero en `ASSETS_DIR` y se recrea el contenedor `api`
- **THEN** el fichero sigue existiendo
