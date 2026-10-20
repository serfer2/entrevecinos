## Why

TK-003 dejó pendiente la `Content-Security-Policy` hasta conocer los orígenes de la API y de las imágenes. Con TK-019/TK-023 ya se conocen: el navegador solo habla con Next y las imágenes llegan por una redirección al almacenamiento, cuyo origen debe estar en `img-src`. Ticket: `docs/product/tickets/00-infra/TK-046-seguridad-content-security-policy.md`.

## What Changes

- `buildCsp()` (función pura) y CSP con *nonce* por petición en `src/proxy.ts`.
- `img-src` con el origen de `STORAGE_PUBLIC_URL` (nueva variable del servicio `web`).
- Renderizado dinámico de todas las páginas (necesario para aplicar el *nonce*).

## Capabilities

### New Capabilities
- `web-security`: política de seguridad de contenidos del frontend.

### Modified Capabilities

## Impact

- `apps/web` (`proxy.ts`, `layout.tsx`, `lib/security/`), `infra/docker-compose.yml`, documentación.
