## Why

HU-18: tras `make dev`, `http://localhost:3000` mostraba solo el marcador de TK-003 («EntreVecinos»), sin enlaces, y no había forma de llegar al registro ni al inicio de sesión. Ticket: `docs/product/tickets/EP-07-mejora-de-funcionalidades-del-mvp/HU-18-acceder-a-la-aplicacion-desde-la-pagina-principal/TK-047-frontend-redirigir-la-raiz.md`.

## What Changes

- `/` deja de ser una página marcador: redirige a `/inicio` con sesión válida y a `/iniciar-sesion` sin ella o si la API falla.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-session`: redirección de la raíz según la sesión.
- `web-skeleton`: el arranque del servicio `web` ya no sirve una página marcador en `/`.

## Impact

- `apps/web` (`src/app/page.tsx`).
