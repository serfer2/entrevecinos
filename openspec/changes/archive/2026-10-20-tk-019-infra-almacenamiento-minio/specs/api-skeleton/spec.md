## MODIFIED Requirements

### Requirement: Configuración por entorno
La configuración SHALL leerse de variables de entorno (`DATABASE_URL`, `CORS_ORIGINS`, `ENVIRONMENT` y las de almacenamiento `STORAGE_*`) y MUST fallar con un error explícito si `DATABASE_URL` no está definida.

#### Scenario: Falta DATABASE_URL
- **WHEN** la aplicación se crea sin `DATABASE_URL` en el entorno
- **THEN** se lanza un error de validación de configuración que nombra `DATABASE_URL`

## REMOVED Requirements

### Requirement: Persistencia de assets
**Reason**: los ficheros pasan al almacenamiento de objetos (`storage`, MinIO).
**Migration**: las imágenes se guardan en el bucket `STORAGE_BUCKET` mediante la API S3 (TK-021); el volumen `api_assets` puede borrarse con `docker volume rm entrevecinos_api_assets`.
