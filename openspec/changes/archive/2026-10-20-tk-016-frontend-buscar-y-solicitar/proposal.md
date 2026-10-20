## Why

HU-05 en la interfaz: encontrar la comunidad, solicitar el acceso, ver el estado de la solicitud y no ver anuncios hasta la aprobación. Ticket: `docs/product/tickets/EP-02-comunidades/HU-05-seleccionar-una-comunidad-y-solicitar-el-acceso/TK-016-frontend-buscar-comunidades-y-solicitar-acceso.md`.

## What Changes

- Página `/comunidades` (búsqueda GET paginada) con la acción de cada resultado según mi membresía.
- *Server Action* `requestAccess` (`201` y `409` muestran el estado; `404` y red, error).
- Componente `Pagination` reutilizable.
- «Mis comunidades» en `/inicio` y aviso de acceso en `/comunidades/[communityId]`.
- El enlace «Comunidades» de la cabecera apunta a `/comunidades`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-communities`: búsqueda, solicitudes de acceso y estado de mis comunidades.

## Impact

- `apps/web`.
