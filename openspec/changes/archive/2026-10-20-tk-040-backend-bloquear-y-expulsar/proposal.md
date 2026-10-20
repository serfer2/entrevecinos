## Why

HU-16: el administrador ve los miembros con su estado y bloquea o expulsa a quien incumple las normas; ese vecino pierde el acceso y sus anuncios dejan de mostrarse. Ticket: `docs/product/tickets/EP-06-administracion-minima/HU-16-gestionar-los-miembros-de-mi-comunidad/TK-040-backend-expulsar-y-bloquear-miembros.md`.

## What Changes

- `PATCH …/memberships/{user_id}` admite `blocked` (bloquear) y `approved` sobre un bloqueado (desbloquear), con protecciones (409).
- `DELETE …/memberships/{user_id}`: expulsión o salida, sin dejar la comunidad sin administrador.
- Listado de membresías sin filtro ordenado por estado y nombre.
- Los anuncios de autores sin membresía aprobada se ocultan en el listado, la búsqueda, el detalle y las imágenes.

## Capabilities

### New Capabilities

### Modified Capabilities
- `community-authorization`: gestión de miembros.

## Impact

- `apps/api`.
