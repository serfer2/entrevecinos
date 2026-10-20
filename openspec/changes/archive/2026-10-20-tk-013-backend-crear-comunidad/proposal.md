## Why

HU-04: un vecino crea la comunidad de su barrio y queda como administrador aprobado. Ticket: `docs/product/tickets/EP-02-comunidades/HU-04-crear-una-comunidad/TK-013-backend-crear-comunidad.md`.

## What Changes

- Dominio `communities` (entidades, roles y estados de membresía, `CommunityNotFound`).
- Base común `NotFoundError` → `404 {"detail": "Recurso no encontrado."}`.
- `POST /v1/communities` y `GET /v1/communities/{community_id}`.

## Capabilities

### New Capabilities
- `community-management`: creación y consulta de comunidades.

### Modified Capabilities

## Impact

- `apps/api` (dominio, aplicación, infraestructura, presentación y pruebas).
