## Why

HU-12: filtrar los anuncios por tipo (y por categoría, según el contrato) y combinarlos con la búsqueda; el filtro por comunidad es la propia ruta. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-12-filtrar-anuncios-por-comunidad-y-tipo/TK-032-backend-filtros-de-anuncios.md`.

## What Changes

- Parámetros `type` (`ListingType`) y `category_id` (UUID) en `GET /v1/communities/{id}/listings`, combinados con `AND` entre sí, con `q` y con la visibilidad.

## Capabilities

### New Capabilities

### Modified Capabilities
- `listing-browsing`: filtros por tipo y categoría.

## Impact

- `apps/api`.
