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

Las variables `NEXT_PUBLIC_*` se incorporan al compilar y llegan al navegador: nunca guardes secretos en ellas.

## Sesión y llamadas a la API

- El navegador nunca recibe el JWT en JavaScript. Los formularios envían los datos a *Server Actions*; estas llaman a la API desde el servidor de Next (`API_INTERNAL_URL`) y guardan el token en la *cookie* `ev_session` (`HttpOnly`, `SameSite=Lax`, `Secure` en producción, misma duración que el token).
- `src/lib/api/server.ts` (`apiFetch`) y `src/features/auth/session.ts` solo se pueden importar en el servidor (`server-only`): importarlos desde un componente de cliente rompe la compilación.
- `apiFetch` nunca lanza excepciones: devuelve `{ ok: true, data }` o `{ ok: false, error }` (`status: 0` si la API no responde).
- `src/components/ui/TextField.tsx`: campo con etiqueta, ayuda y error accesibles, compartido por los formularios.
- `src/features/auth/api.ts` (`userApiFetch`): llamada a la API con el token de la sesión; ante un `401` redirige al inicio de sesión. Úsala en las páginas y acciones privadas.
- `src/components/ui/TextAreaField.tsx`: igual que `TextField` para textos largos.
- `src/lib/forms.ts`: `formText()` (valor de un campo) e `isUuid()` (validar ids de la URL antes de llamar a la API).
- `src/app/(privado)/layout.tsx`: cabecera de la zona privada; `NavLink` marca la sección actual con `aria-current="page"`. El *layout* no comprueba la sesión: cada página llama a `requireUser()`.

## Rutas privadas

Todas las rutas son privadas salvo las de `PUBLIC_ROUTES` (`src/features/auth/routes.ts`: `/`, `/registro` e `/iniciar-sesion`). La protección tiene dos niveles:

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
