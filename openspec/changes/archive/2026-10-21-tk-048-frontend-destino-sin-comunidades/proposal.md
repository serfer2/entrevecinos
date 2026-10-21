## Why

HU-19: un vecino sin comunidades llegaba a `/inicio` tras registrarse o iniciar sesión y tenía que pulsar un enlace más para buscar la suya. Ticket: `docs/product/tickets/EP-07-mejora-de-funcionalidades-del-mvp/HU-19-buscar-comunidades-al-registrarme-o-iniciar-sesion-si-no-pertenezco-a-ninguna/TK-048-frontend-destino-tras-registro-o-login-sin-comunidades.md`.

## What Changes

- `signup` redirige a `/comunidades` en lugar de a `/inicio`.
- `login` sin `next` seguro redirige según `postLoginPath(token)`: `/comunidades` si el usuario no es miembro aprobado de ninguna comunidad activa; si no, `/inicio`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-signup`: destino tras el registro.
- `web-session`: destino tras el inicio de sesión sin `next`.

## Impact

- `apps/web` (`features/auth`).
