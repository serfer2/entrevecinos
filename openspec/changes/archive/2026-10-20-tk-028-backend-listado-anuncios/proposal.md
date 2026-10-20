## Why

HU-10: un miembro aprobado ve los anuncios de su comunidad, del más reciente al más antiguo; quien no lo es, no. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-10-ver-los-anuncios-de-mi-comunidad/TK-028-backend-listado-de-anuncios.md`.

## What Changes

- `GET /v1/communities/{id}/listings` paginado, solo anuncios `active` y `reserved` no eliminados, orden `published_at DESC, id DESC`.
- `ListingQuery` (aplicación) extensible para búsqueda, filtros y orden (TK-030, TK-032, TK-034); hasta entonces `q`, `type`, `category_id`, `sort` y `order` responden `422`.
- Carga sin N+1 (`ListingLoader`).

## Capabilities

### New Capabilities
- `listing-browsing`: listado de anuncios de una comunidad.

### Modified Capabilities

## Impact

- `apps/api`.
