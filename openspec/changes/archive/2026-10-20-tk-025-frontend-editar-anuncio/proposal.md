## Why

HU-08 en la interfaz: el autor modifica su anuncio sin poder dejar vacíos el título ni la descripción, y a los demás no se les ofrece la edición. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-08-editar-mis-anuncios/TK-025-frontend-editar-anuncio.md`.

## What Changes

- Página `/anuncios/[listingId]/editar` con `ListingForm` precargado (datos e imágenes).
- *Server Action* `updateListing`: `PATCH` solo con los campos cambiados y `PUT …/images` si cambió el orden o la portada; avisa de un fallo parcial.
- Enlace «Editar anuncio» en el detalle, solo para el autor (y no en anuncios retirados).

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: edición de anuncios propios.

## Impact

- `apps/web`.
