## Why

HU-02 pide iniciar sesión, mostrar un error genérico y exigir sesión antes de ver el contenido privado. TK-007 dejó la *cookie* de sesión pero sin protección de rutas. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-02-iniciar-sesion/TK-009-frontend-inicio-de-sesion-y-rutas-protegidas.md`.

## What Changes

- Página `/iniciar-sesion` (`LoginForm`, *Server Action* `login`, parámetro `next`, aviso de sesión caducada).
- `src/proxy.ts`: rutas privadas por defecto; sin *cookie* redirige a `/iniciar-sesion?next=…`.
- DAL (`getCurrentUser`, `requireUser`) contra `GET /v1/users/me`.
- `safeNextPath` contra *open redirects*; constantes de rutas (`PUBLIC_ROUTES`, `LOGIN_PATH`, `HOME_PATH`).
- `/inicio` saluda al usuario; `/registro` e `/iniciar-sesion` redirigen a `/inicio` con sesión válida; `error.tsx` del grupo `(privado)`.

## Capabilities

### New Capabilities
- `web-session`: inicio de sesión desde el navegador y protección de las rutas privadas.

### Modified Capabilities

## Impact

- `apps/web` (auth, proxy, páginas, pruebas, README).
