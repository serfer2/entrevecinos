## Context

TK-01 y TK-02 dejaron `db` y `api` en Compose con las redes `data` y `edge`. Este cambio añade el frontend vacío en `edge`, sin acceso a `data`.

## Goals / Non-Goals

**Goals:**
- `web` arranca `healthy` en Compose con recarga en caliente.
- Cabeceras de seguridad equivalentes a Helmet en todas las rutas.
- Imagen de producción mínima (`standalone`) con usuario no root.

**Non-Goals:**
- Pantallas, componentes, cliente de la API, autenticación, diseño visual, pruebas de interfaz, CSP.

## Decisions

- **Scaffold con `create-next-app@16.4.2`:** genera ESLint flat config (`eslint-config-next`), `tsconfig` y el lockfile; después se reorganiza a la estructura del README (`src/styles/globals.css` en lugar de `src/app/globals.css`, sin assets de ejemplo).
- **npm + `package-lock.json`:** sin herramientas extra; `npm ci` en Docker.
- **Cabeceras en `next.config.ts` (`headers()`):** Next sin servidor personalizado no puede usar Helmet. HSTS depende de `NODE_ENV=production`, que se evalúa al construir la configuración en el servidor.
- **Etapas `deps` → `dev` / `build` → `prod`:** `deps` aprovecha la caché de `npm ci`; `prod` copia solo `.next/standalone`, `.next/static` y `public`, y ejecuta `node server.js` con el usuario `node` (uid 1000) de la imagen base.
- **Volúmenes `web_node_modules` y `web_next_cache`:** el *bind mount* de `apps/web` no pisa las dependencias Linux del contenedor ni la caché de compilación.
- **Healthcheck con `wget`:** incluido en Alpine (BusyBox), sin instalar nada.
- **Excepción `!apps/web/src/lib/` en `.gitignore`:** la regla `lib/` de la plantilla Python ignoraría la carpeta `lib` del frontend.

- **Tailwind con `@tailwindcss/postcss` en lugar del loader `@tailwindcss/turbopack` que genera el scaffold de 16.4:** es la integración que documenta Next 16 y la que pide el ticket (`postcss.config.mjs`); funciona con Turbopack y webpack.
- **Sin `cacheComponents` ni `partialPrefetching`:** el scaffold los activa por defecto, pero cambian el modelo de caché y renderizado; se decidirá al implementar las primeras pantallas.
- **`typecheck` = `next typegen && tsc --noEmit`:** los tipos de rutas se generan en `.next/`, que no se versiona; así el comando funciona en un clon limpio.
- **`AGENTS.md` versionado:** `next dev` lo regenera; se versiona para mantener el árbol limpio.
- **Excepción `!apps/web/package-lock.json`:** la regla global `package-lock.json` de `.gitignore` impediría versionar el lockfile que exige `npm ci`.

## Risks / Trade-offs

- [`WATCHPACK_POLLING` consume CPU] → se puede desactivar en Linux nativo.
- [`NEXT_PUBLIC_*` se fija al compilar] → la imagen `prod` recibe la URL como *build arg*; cambiarla exige reconstruir.
- [Volumen `web_node_modules` desactualizado tras cambiar dependencias] → documentar `docker compose ... up -d --build --renew-anon-volumes` o borrar el volumen.
- [CSP pendiente] → se definirá al implementar pantallas.
- [Vulnerabilidad `braces` (alta) en dependencias de desarrollo de ESLint] → solo afecta a herramientas locales; `npm audit --omit=dev` está limpio. Revisar al actualizar ESLint.
