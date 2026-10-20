## Why

HU-07 adjunta fotografías. El README define un almacenamiento compatible con S3 (MinIO en local) y el contrato sirve las imágenes con URL prefirmadas. TK-002 dejó un volumen `api_assets` provisional. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/TK-019-infra-almacenamiento-minio.md`.

## What Changes

- Servicios `storage` (MinIO, `pgsty/minio:RELEASE.2026-08-04T00-00-00Z`) y `storage-init` (bucket privado, usuario y política mínima para la API), volumen `storage_data`.
- Variables de almacenamiento en `.env.example` y en el servicio `api`.
- Puerto S3 publicado solo en `127.0.0.1`; consola mediante *override* opcional.
- **BREAKING (desarrollo):** se retiran el volumen `api_assets` y `ASSETS_DIR`.

## Capabilities

### New Capabilities
- `object-storage`: almacenamiento de objetos local para las imágenes.

### Modified Capabilities

## Impact

- `infra/`, `.env.example`, `apps/api` (configuración y `Dockerfile`), documentación.
