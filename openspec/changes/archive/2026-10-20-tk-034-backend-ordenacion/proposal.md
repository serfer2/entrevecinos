## Why

HU-13: ordenar los anuncios por fecha de publicación o por precio, con los anuncios sin precio al final. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-13-ordenar-anuncios-por-fecha-o-precio/TK-034-backend-ordenacion-de-anuncios.md`.

## What Changes

- Parámetros `sort` (`published_at`, `price`) y `order` (`asc`, `desc`) en `GET /v1/communities/{id}/listings`, combinables con la búsqueda y los filtros.
- Se retira la respuesta 422 provisional para parámetros pendientes: el listado implementa ya todo el contrato.

## Capabilities

### New Capabilities

### Modified Capabilities
- `listing-browsing`: ordenación.

## Impact

- `apps/api`.
