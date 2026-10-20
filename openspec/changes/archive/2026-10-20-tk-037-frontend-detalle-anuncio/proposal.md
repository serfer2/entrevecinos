## Why

HU-14 en la interfaz: la página de detalle muestra toda la información del anuncio y de su anunciante, y será el punto de entrada para editar, eliminar, contactar y retirar. Ticket: `docs/product/tickets/EP-05-detalle-y-contacto/HU-14-consultar-el-detalle-de-un-anuncio/TK-037-frontend-detalle-de-anuncio.md`.

## What Changes

- Página `/anuncios/[listingId]` con galería accesible, tipo, «Reservado», precio, categoría, fechas, descripción y anunciante.
- «Anuncio no disponible» (`not-found.tsx`) para `404` y aviso de acceso para `403`.
- `ListingActions` (vacío) donde los tickets siguientes añaden sus botones.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: detalle de un anuncio.

## Impact

- `apps/web`.
