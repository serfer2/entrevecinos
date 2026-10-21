## Why

HU-20: un miembro de una sola comunidad llegaba a `/inicio` tras iniciar sesión y tenía que pulsar en ella para ver sus anuncios. Ticket: `docs/product/tickets/EP-07-mejora-de-funcionalidades-del-mvp/HU-20-entrar-en-mi-comunidad-al-iniciar-sesion-si-solo-pertenezco-a-una/TK-049-frontend-destino-tras-login-con-una-comunidad.md`.

## What Changes

- `postLoginPath` lleva a `/comunidades/{id}` cuando el usuario es miembro aprobado de una sola comunidad activa; con varias sigue llevando a `/inicio`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-session`: destino tras el inicio de sesión con una sola comunidad.

## Impact

- `apps/web` (`features/auth/destination.ts`).
