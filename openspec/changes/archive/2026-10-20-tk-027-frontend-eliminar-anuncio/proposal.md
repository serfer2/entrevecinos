## Why

HU-09 en la interfaz: el autor elimina su anuncio tras confirmarlo, y desaparece del listado. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-09-eliminar-mis-anuncios/TK-027-frontend-eliminar-anuncio.md`.

## What Changes

- Botón «Eliminar anuncio» en el detalle, solo para el autor, con `ConfirmDialog`.
- *Server Action* `deleteListing` que vuelve a la comunidad con «Anuncio eliminado.» o al detalle con el error.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: eliminación de anuncios propios.

## Impact

- `apps/web`.
