## Why

Las fotografías de HU-07 se suben antes de asociarlas a un anuncio y se leen con permisos y URL prefirmadas. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/TK-021-backend-subida-y-lectura-de-imagenes.md`.

## What Changes

- Puerto `ObjectStorage` y adaptador `S3ObjectStorage` (`boto3`; cliente interno para subir y cliente público para firmar).
- `POST /v1/media` (multipart, campo `file`): tipo por *magic bytes*, máximo 5 MB (413/415/422).
- `GET /v1/media/{asset_id}`: `302` a una URL prefirmada de 300 s si el usuario puede leerla; `403`/`404` si no.
- Configuración `STORAGE_*`, `MEDIA_MAX_BYTES` y `MEDIA_URL_TTL_SECONDS`; dependencias `boto3` y `python-multipart`.

## Capabilities

### New Capabilities
- `media-upload`: subida y lectura de imágenes.

### Modified Capabilities

## Impact

- `apps/api` (dependencias, configuración, dominio, aplicación, infraestructura, presentación y pruebas).
