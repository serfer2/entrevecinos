## Why

HU-30: la galería del detalle no permite ver una fotografía a mayor tamaño. Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-30-ver-las-fotografias-de-un-anuncio-a-pantalla-completa/TK-069-frontend-visor-de-imagenes.md`.

## What Changes

- `Lightbox` genérico en un `<dialog>` modal, con botones, flechas del teclado y gestos táctiles.
- La imagen principal de `ListingGallery` abre el visor («Ampliar imagen N de M»).
- Bloqueo del desplazamiento de la página con un diálogo modal abierto.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: visor de imágenes a pantalla completa en el detalle.

## Impact

- `apps/web` (`components/ui/Lightbox.tsx`, `ListingGallery.tsx`, `styles/globals.css`).
