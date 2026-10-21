## Why

HU-24: el usuario no podía cerrar su sesión, un problema en equipos compartidos. Ticket: `docs/product/tickets/EP-09-cierre-de-sesion/HU-24-cerrar-sesion/TK-055-frontend-cerrar-sesion.md`.

## What Changes

- *Server Action* `logout()`: borra la *cookie* `ev_session` y redirige a `/`.
- Botón «Cerrar sesión» al final de la navegación de la cabecera privada.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-session`: cierre de sesión.

## Impact

- `apps/web` (`features/auth`, `app/(privado)/layout.tsx`). Sin cambios en la API.
