## Why

HU-16 en la interfaz: el administrador ve los miembros con su rol y estado y puede bloquearlos, desbloquearlos o expulsarlos; un miembro sin rol no accede. Ticket: `docs/product/tickets/EP-06-administracion-minima/HU-16-gestionar-los-miembros-de-mi-comunidad/TK-041-frontend-gestion-de-miembros.md`.

## What Changes

- Pestañas «Solicitudes» y «Miembros» en la gestión de la comunidad (`gestion/layout.tsx`).
- Página `/comunidades/[communityId]/gestion/miembros` paginada con filtro por estado (`?estado=`).
- *Server Action* `manageMember` (bloquear, desbloquear, expulsar) con confirmación para bloquear y expulsar.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-community-admin`: gestión de miembros.

## Impact

- `apps/web`.
