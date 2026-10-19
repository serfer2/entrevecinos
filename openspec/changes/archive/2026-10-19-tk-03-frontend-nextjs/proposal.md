## Why

El README define el frontend como React + Next.js 16 + TypeScript + TailwindCSS, organizado en `apps/web/src/` (`app/`, `features/`, `components/`, `lib/`, `styles/`), con las cabeceras de seguridad de Helmet configuradas en Next.js. No existe todavía el proyecto web. Ticket de origen: `docs/product/tickets/00-infra/TK-003-frontend-nextjs.md`.

## What Changes

- Nuevo proyecto `apps/web/` con Next.js 16 (App Router), TypeScript, TailwindCSS 4 y ESLint, `package-lock.json` versionado y `engines.node >= 20.9`.
- Estructura de carpetas del README vacía, con un `layout` y una `page` marcadores sin contenido de producto.
- `next.config.ts` con `output: 'standalone'`, `poweredByHeader: false` y cabeceras de seguridad (HSTS solo en producción).
- Variables `NEXT_PUBLIC_API_BASE_URL` y `API_INTERNAL_URL` (`apps/web/.env.example`).
- `Dockerfile` con etapas `deps`, `dev`, `build` y `prod` (no root), `.dockerignore`.
- Servicio `web` y volúmenes `web_node_modules` y `web_next_cache` en `infra/docker-compose.yml`; `WEB_PORT` y `NEXT_PUBLIC_API_BASE_URL` en `.env.example`.
- `.gitignore`: excepciones para `apps/web/src/lib/` (la regla `lib/` de la plantilla de Python la ignoraría) y para `apps/web/package-lock.json` (la regla global `package-lock.json` impediría versionarlo).

## Capabilities

### New Capabilities
- `web-skeleton`: proyecto Next.js configurado y ejecutable en Docker: página marcador, Tailwind operativo con recarga, cabeceras de seguridad, imagen de producción no root y estructura de carpetas sin implementación.

### Modified Capabilities

## Impact

- Código nuevo en `apps/web/`; cambios en `infra/docker-compose.yml`, `.env.example`, `.gitignore` e `infra/README.md`.
- Nuevas dependencias: Node.js 22 (imagen), Next.js 16, React 19, TailwindCSS 4, ESLint.
