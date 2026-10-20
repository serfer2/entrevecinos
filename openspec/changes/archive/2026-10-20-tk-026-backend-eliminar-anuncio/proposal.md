## Why

HU-09: el autor retira un anuncio que ya no es válido y deja de aparecer en cualquier lectura. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-09-eliminar-mis-anuncios/TK-026-backend-eliminar-anuncio.md`.

## What Changes

- `DELETE /v1/listings/{listing_id}`: borrado lógico (`deleted_at`, `status = deleted`) por el autor, un gestor de la comunidad o `platform_admin`.
- Filtro «no eliminado» por defecto en todas las lecturas de anuncios.

## Capabilities

### New Capabilities
- `listing-deletion`: borrado lógico de anuncios.

### Modified Capabilities

## Impact

- `apps/api`.
