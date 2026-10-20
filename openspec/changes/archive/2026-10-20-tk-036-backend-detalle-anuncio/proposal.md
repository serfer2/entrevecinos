## Why

HU-14: ver la información completa de un anuncio y de su anunciante, y un «no disponible» claro si se eliminó o retiró. Ticket: `docs/product/tickets/EP-05-detalle-y-contacto/HU-14-consultar-el-detalle-de-un-anuncio/TK-036-backend-detalle-de-anuncio.md`.

## What Changes

- `GET /v1/listings/{listing_id}` con la regla `ListingVisibility`.
- La lectura de imágenes (TK-021) usa la misma regla en lugar de su propia consulta.
- Los anuncios de cuentas eliminadas dejan de mostrarse en cualquier lectura.

## Capabilities

### New Capabilities
- `listing-detail`: detalle de un anuncio y su visibilidad.

### Modified Capabilities
- `media-upload`: la lectura de una imagen sigue la visibilidad del anuncio que la usa.

## Impact

- `apps/api`.
