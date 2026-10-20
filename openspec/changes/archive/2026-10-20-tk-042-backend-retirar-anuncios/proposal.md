## Why

HU-17: el administrador retira los anuncios inapropiados, que dejan de verse en el listado y las búsquedas; un miembro sin rol no puede hacerlo. Ticket: `docs/product/tickets/EP-06-administracion-minima/HU-17-retirar-anuncios-problematicos/TK-042-backend-retirar-anuncios.md`.

## What Changes

- `PATCH /v1/listings/{id}/status` para retirar (`hidden`) y restaurar (`active`) por moderación.
- Migración `0006`: `listing.hidden_by` y `listing.hidden_at`.

## Capabilities

### New Capabilities
- `listing-moderation`: retirada y restauración de anuncios.

### Modified Capabilities

## Impact

- `apps/api`.
