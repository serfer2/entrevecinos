## Why

HU-08: el autor modifica título, descripción, categoría, tipo, precio o fotografías de su anuncio, sin dejar vacíos el título ni la descripción; nadie más puede editarlo. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-08-editar-mis-anuncios/TK-024-backend-editar-anuncio-e-imagenes.md`.

## What Changes

- `PATCH /v1/listings/{id}`: actualización parcial con la coherencia de precio y moneda sobre el resultado.
- `PUT /v1/listings/{id}/images`: sustituye el conjunto de imágenes (orden y portada).
- Regla común de edición: solo el autor, todavía miembro aprobado, y anuncio no retirado (`403` con mensaje propio).

## Capabilities

### New Capabilities
- `listing-editing`: edición de anuncios propios.

### Modified Capabilities

## Impact

- `apps/api`.
