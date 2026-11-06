## Why

HU-32: la moderación se llama «Retirar», un verbo que se confunde con «Eliminar» y «Marcar como finalizado». Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-32-entender-que-hace-la-moderacion-de-un-anuncio/TK-072-frontend-ocultar-anuncio.md`.

## What Changes

- «Ocultar» en botón, confirmación, avisos y página de anuncio no disponible.
- `?retirado=1` → `?ocultado=1`.
- Mensaje `ListingLocked.RETIRED` de la API y su reconocimiento en `lockedMessage`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-community-admin`: «Ocultar y restaurar anuncios desde el detalle».
- `web-listings`: mensaje de anuncio no disponible.

## Impact

- `apps/web` (`ListingActions.tsx`, `comunidades/[communityId]/page.tsx`, `anuncios/[listingId]/not-found.tsx`, `features/listings/actions.ts`, `form.ts`), `apps/api` (`domain/listings/errors.py`). Sin cambios de comportamiento.
