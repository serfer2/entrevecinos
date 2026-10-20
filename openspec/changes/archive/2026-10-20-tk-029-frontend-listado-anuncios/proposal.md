## Why

HU-10 en la interfaz: la página de una comunidad muestra sus anuncios con título, tipo, precio, fotografía y fecha, los más recientes primero. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-10-ver-los-anuncios-de-mi-comunidad/TK-029-frontend-listado-de-anuncios.md`.

## What Changes

- Listado paginado (24 por página) en `/comunidades/[communityId]` para miembros aprobados, con estado vacío.
- `ListingCard` (portada diferida, tipo, precio o «Gratis», «Reservado», fecha) en una cuadrícula responsive.
- Formateadores de precio y fecha, y `ListingSearchParams` (lectura de la URL ampliable por búsqueda, filtros y orden).

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: listado de anuncios de la comunidad.

## Impact

- `apps/web`.
