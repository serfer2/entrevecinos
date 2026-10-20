## Why

HU-06 en la interfaz: el administrador ve las solicitudes pendientes y las aprueba o rechaza; un miembro sin ese rol no tiene acceso. Ticket: `docs/product/tickets/EP-02-comunidades/HU-06-aprobar-o-rechazar-solicitudes-de-acceso/TK-018-frontend-gestion-de-solicitudes.md`.

## What Changes

- Página `/comunidades/[communityId]/gestion/solicitudes` (paginada) con «Aprobar» y «Rechazar» (con confirmación).
- *Server Action* `reviewRequest` que redirige a la misma página con el resultado.
- Enlace «Gestionar comunidad» para `community_admin`.
- Componentes compartidos `Forbidden` y `ConfirmDialog`.

## Capabilities

### New Capabilities
- `web-community-admin`: gestión de la comunidad desde la interfaz.

### Modified Capabilities

## Impact

- `apps/web`.
