# Web de EntreVecinos

Frontend con **Next.js 16** (App Router), **React 19**, **TypeScript** y **TailwindCSS 4**.

## Estructura

```
src/
├── app/          # rutas del App Router (layout y página marcadores por ahora)
├── features/     # código por funcionalidad: auth, communities, listings, messaging
├── components/   # componentes compartidos
├── lib/          # utilidades y cliente de la API
└── styles/       # globals.css (importa Tailwind)
```

El alias `@/*` apunta a `src/*`.

## Con Docker (recomendado)

Desde la raíz del repositorio, con `.env` creado a partir de `.env.example`:

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE up -d --build web          # levanta db, api y web
$COMPOSE exec web npm run lint
$COMPOSE exec web npm run typecheck
$COMPOSE exec web npm run test
```

- http://localhost:3000 (puerto configurable con `WEB_PORT`).
- `apps/web` se monta en el contenedor y la página se recarga al guardar.
- `node_modules` y `.next` viven en volúmenes con nombre del contenedor. Tras cambiar dependencias, el volumen conserva las antiguas: elimínalo y reconstruye.

  ```bash
  $COMPOSE stop web && $COMPOSE rm -f web
  docker volume rm entrevecinos_web_node_modules
  $COMPOSE up -d --build web
  ```

## Sin Docker

Requiere Node.js ≥ 20.9.

```bash
cd apps/web
cp .env.example .env.local   # ajusta NEXT_PUBLIC_API_BASE_URL si hace falta
npm ci
npm run dev                  # http://localhost:3000
npm run lint
npm run typecheck
npm run test                 # Vitest + Testing Library (Node ≥ 22.12)
npm run build && npm run start
```

## Variables de entorno

| Variable | Ámbito | Uso | Valor local |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Navegador | URL de la API que usa el navegador | `http://localhost:8000/v1` |
| `API_INTERNAL_URL` | Servidor (Next) | URL de la API dentro de la red de Docker | `http://api:8000/v1` |
| `STORAGE_PUBLIC_URL` | Servidor (Next) | Origen de las URL prefirmadas de las imágenes; se permite en `img-src` de la CSP. Obligatoria: sin ella el servidor no arranca. En producción, la URL del servicio S3 o de su CDN | `http://localhost:9000` |

Las variables `NEXT_PUBLIC_*` se incorporan al compilar y llegan al navegador: nunca guardes secretos en ellas.

## Sesión y llamadas a la API

- El navegador nunca recibe el JWT en JavaScript. Los formularios envían los datos a *Server Actions*; estas llaman a la API desde el servidor de Next (`API_INTERNAL_URL`) y guardan el token en la *cookie* `ev_session` (`HttpOnly`, `SameSite=Lax`, `Secure` en producción, misma duración que el token).
- `src/lib/api/server.ts` (`apiFetch`) y `src/features/auth/session.ts` solo se pueden importar en el servidor (`server-only`): importarlos desde un componente de cliente rompe la compilación.
- `apiFetch` nunca lanza excepciones: devuelve `{ ok: true, data }` o `{ ok: false, error }` (`status: 0` si la API no responde).
- `src/components/ui/TextField.tsx`: campo con etiqueta, ayuda y error accesibles, compartido por los formularios.
- `src/features/auth/api.ts` (`userApiFetch`): llamada a la API con el token de la sesión; ante un `401` redirige al inicio de sesión. Úsala en las páginas y acciones privadas.
- `src/components/ui/TextAreaField.tsx`: igual que `TextField` para textos largos.
- `src/components/ui/Forbidden.tsx`: aviso común para las páginas a las que la API responde `403`.
- `src/components/ui/ConfirmDialog.tsx`: botón que pide confirmación en un `<dialog>` modal antes de enviar su formulario (sin JavaScript envía directamente).
- `src/components/ui/Pagination.tsx`: «Anterior / Siguiente» de los listados; recibe `hrefFor(page)`.
- Imágenes: el navegador nunca habla con la API. Las sube la *Server Action* `uploadImage` (una por llamada; `serverActions.bodySizeLimit = "6mb"`) y las lee la ruta `GET /media/[assetId]`, que pide a la API la URL prefirmada sin seguir la redirección y redirige a ella (`403`/`404` → `404`). Usa `mediaSrc()` (`src/lib/media.ts`) para pintarlas con `<img>`.
- `src/features/media/components/ImagePicker.tsx`: subida en serie, reordenar y quitar; envía los ids en campos ocultos `image_asset_ids`.
- `src/features/listings/components/ListingForm.tsx`: formulario de anuncio (publicar y editar).
- Los ficheros `"use server"` solo pueden exportar funciones `async`: constantes y utilidades van en otro módulo (p. ej. `features/communities/admin/paths.ts`). Lo comprueba `src/lib/server-actions.test.ts`.
- `src/lib/forms.ts`: `formText()` (valor de un campo) e `isUuid()` (validar ids de la URL antes de llamar a la API).
- `src/app/(privado)/layout.tsx`: cabecera de la zona privada; `NavLink` marca la sección actual con `aria-current="page"`. El *layout* no comprueba la sesión: cada página llama a `requireUser()`.

## Rutas privadas

Todas las rutas son privadas salvo las de `PUBLIC_ROUTES` (`src/features/auth/routes.ts`: `/`, `/registro`, `/iniciar-sesion`, `/verificar-correo` y `/verificar-correo/error`). La protección tiene dos niveles:

1. `src/proxy.ts`: si no existe la *cookie* `ev_session`, redirige a `/iniciar-sesion?next=<ruta>`. No valida el token.
2. DAL (`src/features/auth/dal.ts`): `requireUser()` valida la sesión contra `GET /v1/users/me` (una vez por petición) y, si el token ya no es válido, redirige a `/iniciar-sesion?motivo=sesion-caducada`.

Para crear una página privada, colócala en `src/app/(privado)/` y llama a `requireUser()` en la propia página (y en cada *Server Action* privada), no solo en el *layout*:

```tsx
import { requireUser } from "@/features/auth/dal";

export default async function MiPagina() {
  const user = await requireUser();
  return <h1>Hola, {user.full_name}</h1>;
}
```

`safeNextPath()` (`src/features/auth/redirect.ts`) valida el parámetro `next` para que solo se redirija a rutas internas.

## Registro y validación del correo

1. `/registro`: la *Server Action* `signup` crea la cuenta pero **no** inicia la sesión; `SignupForm` sustituye el formulario por el aviso «Te hemos enviado un correo a {email}…». En desarrollo, el correo se ve en Mailpit: http://localhost:8025.
2. El enlace del correo abre `GET /verificar-correo?token=…` (`src/app/verificar-correo/route.ts`), un *route handler* porque las páginas de servidor no pueden escribir *cookies*. Valida el token con la API, crea la sesión y redirige con `303` a `/comunidades`. La respuesta lleva `Cache-Control: no-store` y `Referrer-Policy: no-referrer` (este, en `next.config.ts`, porque la cabecera global lo sobrescribiría). El `Location` es relativo: `request.url` lleva el host interno del servidor.
3. Si falla: caducado → `/verificar-correo/error?motivo=caducado&email=…`; enlace ya usado → `/comunidades` con sesión o `/iniciar-sesion?motivo=correo-validado` sin ella (cubre el doble clic y los escáneres de correo); sin token o no válido → `motivo=invalido`; error de la API → `motivo=error`.
4. `/iniciar-sesion` con una cuenta sin validar muestra «Tienes que validar tu correo electrónico antes de iniciar sesión.».
5. `ResendVerificationButton` (*Server Action* `resendVerification`) pide otro enlace en tres sitios: el registro con un correo pendiente, la página de enlace caducado y el inicio de sesión sin validar. Se renderiza fuera del formulario principal (no se pueden anidar formularios).

## Pruebas

Vitest + Testing Library (`vitest.config.mts`). Las pruebas viven junto al código (`*.test.ts(x)`). Los formularios reciben su *Server Action* por *props*, así que se prueban con una acción simulada; las acciones se prueban simulando `apiFetch`, `next/headers` y `next/navigation`.

## Cabeceras de seguridad

`next.config.ts` añade a todas las rutas `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`, desactiva `X-Powered-By` y, solo en producción, `Strict-Transport-Security`. La `Content-Security-Policy` se definirá al implementar las pantallas.

## Imagen de producción

```bash
docker build --target prod -t entrevecinos-web:prod \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/v1 apps/web
docker run --rm -p 3001:3000 entrevecinos-web:prod
```

Usa la salida `standalone` de Next y se ejecuta con el usuario `node` (no root).

## Content-Security-Policy

`src/proxy.ts` genera en cada petición un *nonce* y la cabecera `Content-Security-Policy` (construida por `buildCsp()` en `src/lib/security/csp.ts`), y la pone en la petición (Next la lee para aplicar el *nonce* a sus scripts) y en la respuesta. Por eso el *layout* raíz llama a `connection()`: todas las páginas se renderizan por petición.

- Producción: `script-src 'self' 'nonce-…' 'strict-dynamic'`, estilos con *nonce*, sin `unsafe-*`; `upgrade-insecure-requests` solo si `STORAGE_PUBLIC_URL` es HTTPS (así la imagen de producción se puede probar en local con `http://localhost:9000`).
- Desarrollo: además `'unsafe-eval'`, `'unsafe-inline'` en estilos y `ws:` (recarga en caliente).
- `img-src 'self' data: <origen de STORAGE_PUBLIC_URL>`: las imágenes llegan por `/media/<id>`, que redirige a la URL prefirmada del almacenamiento.
- Al añadir un origen externo (fuentes, analítica…), amplía la política en el mismo cambio.
