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
```

- http://localhost:3000 (puerto configurable con `WEB_PORT`).
- `apps/web` se monta en el contenedor y la página se recarga al guardar.
- `node_modules` y `.next` viven en volúmenes del contenedor. Tras cambiar dependencias, recrea el volumen: `$COMPOSE up -d --build --renew-anon-volumes web` o `docker volume rm entrevecinos_web_node_modules`.

## Sin Docker

Requiere Node.js ≥ 20.9.

```bash
cd apps/web
cp .env.example .env.local   # ajusta NEXT_PUBLIC_API_BASE_URL si hace falta
npm ci
npm run dev                  # http://localhost:3000
npm run lint
npm run typecheck
npm run build && npm run start
```

## Variables de entorno

| Variable | Ámbito | Uso | Valor local |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Navegador | URL de la API que usa el navegador | `http://localhost:8000/v1` |
| `API_INTERNAL_URL` | Servidor (Next) | URL de la API dentro de la red de Docker | `http://api:8000/v1` |

Las variables `NEXT_PUBLIC_*` se incorporan al compilar y llegan al navegador: nunca guardes secretos en ellas.

## Cabeceras de seguridad

`next.config.ts` añade a todas las rutas `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`, desactiva `X-Powered-By` y, solo en producción, `Strict-Transport-Security`. La `Content-Security-Policy` se definirá al implementar las pantallas.

## Imagen de producción

```bash
docker build --target prod -t entrevecinos-web:prod \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/v1 apps/web
docker run --rm -p 3001:3000 entrevecinos-web:prod
```

Usa la salida `standalone` de Next y se ejecuta con el usuario `node` (no root).
