## Why

HU-04 necesita un formulario para crear la comunidad, y la zona privada no tiene navegación común. Ticket: `docs/product/tickets/EP-02-comunidades/HU-04-crear-una-comunidad/TK-014-frontend-crear-comunidad-y-navegacion.md`.

## What Changes

- Cabecera de la zona privada (`(privado)/layout.tsx`) con `NavLink` y `aria-current`.
- `features/communities`: esquema, *Server Action* `createCommunity`, `CommunityForm`.
- Páginas `/comunidades/nueva` y `/comunidades/[communityId]` (marcador con el nombre).
- `TextAreaField` y `userApiFetch` (llamada autenticada que redirige al expirar la sesión).

## Capabilities

### New Capabilities
- `web-communities`: pantallas de comunidades y navegación privada.

### Modified Capabilities

## Impact

- `apps/web`.
