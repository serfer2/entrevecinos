# TK-046 · Seguridad: `Content-Security-Policy` del frontend

| Campo | Valor |
|---|---|
| **Tipo** | Seguridad / frontend |
| **Componente** | `apps/web/` (`src/proxy.ts`, `src/lib/security/csp.ts`, `app/layout.tsx`), `infra/docker-compose.yml` (variable del servicio `web`) |
| **Historia** | Transversal (requisito de seguridad, README §2.5); necesaria desde HU-07 por las imágenes |
| **Prioridad** | Alta (antes de cerrar la Épica 3) |
| **Depende de** | TK-003 (cabeceras de seguridad), TK-019 (origen público del almacenamiento), TK-023 (ruta `/media/[assetId]`) |
| **Referencias** | `readme.md` §2.5; TK-003 §3.3 (`next.config.ts`) y §8 (CSP pendiente); guía oficial de Next.js «Content Security Policy» (nonce en *Proxy*) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-003 añadió las cabeceras de seguridad equivalentes a Helmet, pero dejó la `Content-Security-Policy` para cuando se conocieran los orígenes de la API y de las imágenes. Con TK-019 y TK-023 ya se conocen: el navegador solo habla con Next (la API se llama desde el servidor), y las imágenes llegan por `/media/<id>`, que responde con una redirección `302` a una URL prefirmada del almacenamiento (`http://localhost:9000` en local, el servicio S3 en producción). La CSP también se aplica al destino de una redirección, así que ese origen debe estar en `img-src` o las imágenes no se cargarán.

**Objetivo:** definir una CSP estricta con *nonce* para scripts y estilos, que permita las imágenes del almacenamiento configurado y que funcione en desarrollo y en producción.

## 2. Alcance

**Incluye**
- Generación de la CSP en `src/proxy.ts` con un *nonce* por petición (guía oficial de Next.js).
- `img-src` con el origen público del almacenamiento, leído de una variable de entorno.
- Variable `STORAGE_PUBLIC_URL` en el servicio `web` (mismo valor que `STORAGE_PUBLIC_ENDPOINT` de la API, TK-019).
- Renderizado dinámico de todas las páginas, necesario para aplicar el *nonce*.
- Pruebas unitarias del constructor de la política y comprobación en el navegador sin violaciones.

**No incluye**
- `report-uri` / `report-to` y recogida de informes de violaciones (post-MVP, asumido).
- Cabeceras de la API (no sirve HTML; las gestiona TK-002).

## 3. Requisitos técnicos

### 3.1 Política

`src/lib/security/csp.ts` exporta `buildCsp({ nonce, isDev, storageOrigin })` (función pura, probada aparte):

```text
default-src 'self';
script-src 'self' 'nonce-<nonce>' 'strict-dynamic' [dev: 'unsafe-eval'];
style-src 'self' [dev: 'unsafe-inline' | prod: 'nonce-<nonce>'];
img-src 'self' data: <storageOrigin>;
font-src 'self';
connect-src 'self' [dev: ws:];
object-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none';
[prod: upgrade-insecure-requests;]
```

- `storageOrigin` es solo el origen (`esquema://host:puerto`) de `STORAGE_PUBLIC_URL`, calculado con `new URL(...).origin`; nunca una ruta ni un comodín. Si la variable falta o no es una URL válida, el arranque falla (mejor que una CSP que bloquea todas las imágenes sin avisar).
- `connect-src 'self'`: el navegador no llama a la API directamente (cookie `httpOnly` y *Server Actions*). En desarrollo se añade `ws:` para la recarga en caliente.
- `upgrade-insecure-requests` solo en producción: en local las URL prefirmadas son `http://localhost:9000`.
- `frame-ancestors 'none'` duplica a `X-Frame-Options: DENY` (TK-003), que se mantiene para navegadores antiguos.
- `next/font` con fuentes autoalojadas encaja en `font-src 'self'`; si se añade otro origen (fuentes, analítica), se amplía la política en el mismo cambio.

### 3.2 `src/proxy.ts`

- Para cada petición que pasa por el *matcher* actual: genera el *nonce* (`Buffer.from(crypto.randomUUID()).toString("base64")`), construye la política y la pone en la cabecera `Content-Security-Policy` de la **petición** (Next extrae el *nonce* de ahí al renderizar) y de la **respuesta**, junto con `x-nonce`.
- Se conserva la lógica de redirección al inicio de sesión de TK-008; las redirecciones no necesitan CSP.
- La CSP no se define en `next.config.ts` (`headers()`), porque allí no puede variar por petición; el resto de cabeceras de TK-003 se quedan donde están.

### 3.3 Renderizado dinámico

- El *nonce* solo se aplica a páginas renderizadas por petición. El *layout* raíz lee `headers()` (`x-nonce`) o llama a `connection()`, de modo que todas las páginas se renderizan de forma dinámica (asumido: en el MVP casi todas dependen ya de la sesión; las públicas son pocas y ligeras).
- Comprobar en `next build` que ninguna ruta queda como estática (`○`).

### 3.4 Variables

- `infra/docker-compose.yml`, servicio `web`: `STORAGE_PUBLIC_URL: http://localhost:${STORAGE_HOST_PORT:-9000}`.
- Documentarla en `apps/web/README.md` y en `.env.example` si se expone como configurable (asumido: en producción es la URL del servicio S3 o de su CDN).

### 3.5 Pruebas

- `buildCsp`: producción sin `unsafe-*` y con `upgrade-insecure-requests`; desarrollo con `unsafe-eval`, `unsafe-inline` en estilos y `ws:`; `img-src` con el origen exacto; origen con ruta → solo el origen.
- `proxy`: la respuesta lleva `Content-Security-Policy` con un *nonce* distinto en cada petición; sin sesión en ruta privada sigue redirigiendo.

## 4. Criterios de aceptación

**AC1 — Cabecera presente**
- **Given** `make dev`
- **When** ejecuto `curl -sI http://localhost:3000/iniciar-sesion`
- **Then** la respuesta incluye `Content-Security-Policy` con `script-src 'self' 'nonce-…' 'strict-dynamic'` e `img-src 'self' data: http://localhost:9000`, y el *nonce* cambia en cada petición

**AC2 — Imágenes del almacenamiento**
- **Given** un anuncio con fotografías (TK-023)
- **When** abro su detalle y el listado de la comunidad
- **Then** las imágenes se cargan (redirección `302` a `localhost:9000`) y la consola del navegador no muestra violaciones de CSP

**AC3 — La aplicación funciona con la política activa**
- **Given** la política activa en desarrollo y en la imagen de producción (`next build` + `next start`)
- **When** recorro registro, inicio de sesión, perfil, comunidades, publicación con fotos y detalle
- **Then** no hay violaciones de CSP en la consola y los formularios (*Server Actions*) funcionan

**AC4 — Bloqueo de orígenes no permitidos**
- **Given** la política activa
- **When** inyecto en la consola un `<img src="https://example.com/x.png">` o un `<script>` sin *nonce*
- **Then** el navegador los bloquea y lo informa en la consola

## 5. Plan de tareas

1. `buildCsp` con pruebas unitarias.
2. *Nonce* y cabeceras en `src/proxy.ts`; renderizado dinámico en el *layout* raíz.
3. Variable `STORAGE_PUBLIC_URL` en Compose y documentación.
4. Recorrido completo en desarrollo y con la imagen de producción; verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -sI http://localhost:3000/iniciar-sesion | grep -i content-security-policy
curl -sI http://localhost:3000/iniciar-sesion | grep -i content-security-policy   # otro nonce
# Navegador: DevTools > Consola sin "Refused to load…"; DevTools > Red: /media/<id> → 302 → localhost:9000 (200)
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
$COMPOSE exec web npm run build   # ninguna ruta estática (○)
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Sin `unsafe-inline` ni `unsafe-eval` en producción.
- [ ] El comentario de `next.config.ts` sobre la CSP pendiente se actualiza para apuntar a `src/proxy.ts`.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Renderizado dinámico obligatorio:** impide la caché estática de las páginas públicas. Aceptable en el MVP; alternativa: CSP con *hashes* (`experimental.sri`) para las páginas estáticas.
- **Origen de las imágenes en producción:** si se sirve a través de una CDN, `STORAGE_PUBLIC_URL` debe apuntar a ella, o las imágenes se bloquearán.
- **Bibliotecas que inyectan estilos en línea:** con `style-src` por *nonce* en producción pueden fallar; revisar al añadir dependencias de interfaz.
