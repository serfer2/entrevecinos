## Why

HU-09b: el autor marca su anuncio como reservado, quita la reserva o lo da por finalizado. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-09b-marcar-mi-anuncio-como-reservado-o-finalizado/TK-044-backend-reservar-y-finalizar-anuncio.md`.

## What Changes

- `PATCH /v1/listings/{id}/status` admite las transiciones del autor: `active ↔ reserved` y `active | reserved → completed` (final).
- Editar un anuncio `completed` (datos o imágenes) responde `403`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `listing-moderation`: transiciones de estado del autor.

## Impact

- `apps/api`.
