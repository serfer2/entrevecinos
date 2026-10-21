## Why

HU-23: cada usuario puede tener como mucho una comunidad pendiente de aprobación. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-23-tener-una-sola-comunidad-pendiente-de-aprobacion-a-la-vez/TK-053-backend-una-comunidad-pendiente-por-usuario.md`.

## What Changes

- Migración `0007`: índice único parcial `uq_community_one_pending_per_creator` sobre `community(created_by) WHERE NOT is_active`.
- `POST /v1/communities` responde `409` si el usuario ya tiene una comunidad pendiente.
- Contrato (`409` en `createCommunity`) y `docs/api/README.md`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `community-management`: límite de una comunidad pendiente por usuario.
- `community-persistence`: el índice único parcial.

## Impact

- `apps/api` (migración `0007`, área `communities`, manejador de errores), `docs/api`.
