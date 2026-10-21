# web-skeleton Specification

## Purpose
Proyecto web Next.js 16 (`apps/web/`) y su servicio `web` en `infra/docker-compose.yml`.
## Requirements
### Requirement: Tailwind con recarga en caliente
Las clases de TailwindCSS SHALL aplicarse a la página y los cambios en `apps/web/src` SHALL reflejarse sin reiniciar el contenedor.

#### Scenario: Cambio de clase
- **WHEN** se añade una clase de Tailwind (p. ej. `text-red-600`) a la página marcador y se guarda
- **THEN** el CSS servido incluye la regla de esa clase sin reiniciar el contenedor

### Requirement: Cabeceras de seguridad
Todas las respuestas SHALL incluir `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` y `Permissions-Policy`, y MUST NOT incluir `X-Powered-By`. `Strict-Transport-Security` SHALL enviarse solo en producción.

#### Scenario: Cabeceras en desarrollo
- **WHEN** se ejecuta `curl -I http://localhost:3000`
- **THEN** aparecen las cabeceras de seguridad, no aparece `X-Powered-By` ni `Strict-Transport-Security`

#### Scenario: HSTS en producción
- **WHEN** se consulta la imagen `prod`
- **THEN** la respuesta incluye `Strict-Transport-Security: max-age=63072000; includeSubDomains`

### Requirement: Imagen de producción
La etapa `prod` SHALL generarse con `output: 'standalone'`, ejecutarse con un usuario distinto de root y responder en el puerto 3000.

#### Scenario: Build de producción
- **WHEN** se construye con `docker build --target prod` y se ejecuta la imagen
- **THEN** responde 200 en el puerto 3000 e `id -u` es distinto de 0

### Requirement: Estructura sin implementación
`apps/web/src` SHALL contener `app/`, `features/{auth,communities,listings,messaging}`, `components/`, `lib/` y `styles/`; el único código de producto MUST ser el `layout` y la `page` marcadores, y `npm run lint` y `npm run typecheck` SHALL pasar.

#### Scenario: Revisión de la estructura
- **WHEN** se revisa `apps/web/src` y se ejecutan `npm run lint` y `npm run typecheck`
- **THEN** existen las carpetas indicadas, versionadas con `.gitkeep`, y ambos comandos terminan sin errores

### Requirement: Servicio web en Compose
El servicio `web` SHALL construirse desde `apps/web/Dockerfile` (etapa `dev`), depender de `api` sano, estar solo en la red `edge` y publicar `${WEB_PORT:-3000}`; su raíz SHALL llevar a una pantalla de la aplicación (ver `web-session`).

#### Scenario: Arranque del contenedor
- **WHEN** se ejecuta `docker compose --env-file .env -f infra/docker-compose.yml up -d --build web`
- **THEN** el contenedor `web` queda `healthy` y `http://localhost:3000` redirige a `/iniciar-sesion`, que devuelve 200

