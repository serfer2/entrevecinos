## Why

HU-07 en la interfaz: formulario para publicar un anuncio con fotografías. El navegador no tiene el token (cookie `httpOnly`), así que la subida y la lectura de imágenes pasan por el servidor de Next. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/TK-023-frontend-publicar-anuncio.md`.

## What Changes

- Ruta `GET /media/[assetId]` que reenvía la redirección de la API a la URL prefirmada.
- *Server Action* `uploadImage` (una imagen por llamada, `bodySizeLimit = 6mb`) e `ImagePicker` (subida en serie, reordenar, quitar, máximo 10).
- `listingSchema`, `ListingForm` (reutilizable en la edición) y *Server Action* `publishListing`.
- Página `/comunidades/[communityId]/anuncios/nuevo` y botón «Publicar anuncio» para miembros aprobados.
- `apiFetch` admite `FormData` y expone el cuerpo del error (`payload`).

## Capabilities

### New Capabilities
- `web-listings`: pantallas de anuncios.

### Modified Capabilities

## Impact

- `apps/web`.
