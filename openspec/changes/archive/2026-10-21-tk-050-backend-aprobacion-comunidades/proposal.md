## Why

HU-21: las comunidades nuevas no deben estar disponibles hasta que un `platform_admin` las apruebe. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-21-aprobar-las-comunidades-nuevas-antes-de-activarlas/TK-050-backend-aprobacion-de-comunidades.md`.

## What Changes

- `POST /v1/communities` crea la comunidad con `is_active: false` (pendiente de aprobación).
- `GET /v1/admin/communities` y `PATCH /v1/admin/communities/{id}` (solo `is_active: true`) pasan al MVP, solo para `platform_admin`.
- Contrato y tabla de cambios de `docs/api/README.md`.

## Capabilities

### New Capabilities
- `community-approval`: listado y aprobación de comunidades por un `platform_admin`.

### Modified Capabilities
- `community-management`: la creación deja la comunidad pendiente.

## Impact

- `apps/api` (área `communities`, router `admin`), `docs/api`. Sin migración: se reutiliza `community.is_active`.
