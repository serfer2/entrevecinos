## 1. Proyecto

- [x] 1.1 Generar `apps/web` con `create-next-app@16.4.2` (TypeScript, Tailwind, ESLint, App Router, `src/`, alias `@/*`, npm)
- [x] 1.2 Reorganizar a la estructura del ticket: `styles/globals.css`, carpetas con `.gitkeep`, eliminar assets de ejemplo
- [x] 1.3 Layout (`<html lang="es">`) y página marcadores
- [x] 1.4 Scripts `dev`, `build`, `start`, `lint`, `typecheck` y `engines.node`

## 2. Configuración

- [x] 2.1 `next.config.ts`: `standalone`, `poweredByHeader: false`, cabeceras de seguridad y HSTS en producción
- [x] 2.2 `apps/web/.env.example` con `NEXT_PUBLIC_API_BASE_URL` y `API_INTERNAL_URL`
- [x] 2.3 `.gitignore`: excepción `!apps/web/src/lib/`; `node_modules/` y `.next/` cubiertos

## 3. Docker

- [x] 3.1 `apps/web/Dockerfile` (`deps`, `dev`, `build`, `prod`) y `.dockerignore`
- [x] 3.2 Servicio `web` y volúmenes en `infra/docker-compose.yml`; `WEB_PORT` y `NEXT_PUBLIC_API_BASE_URL` en `.env.example`

## 4. Documentación

- [x] 4.1 `apps/web/README.md` (con y sin Docker) y actualizar `infra/README.md`

## 5. Verificación

- [x] 5.1 `web` healthy y página marcador en `localhost:3000` (AC1)
- [x] 5.2 Recarga de Tailwind sin reiniciar (AC2)
- [x] 5.3 Cabeceras de seguridad y sin `X-Powered-By` (AC3)
- [x] 5.4 Imagen `prod` standalone no root responde en 3000 (AC4)
- [x] 5.5 Estructura, `lint`, `typecheck` y `build` (AC5)
