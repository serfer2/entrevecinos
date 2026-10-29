# AGENTS.md

Instrucciones para agentes de código que trabajan en este repositorio. La documentación para personas está en `readme.md`, `apps/api/README.md`, `apps/web/README.md` e `infra/README.md`; aquí solo lo necesario para trabajar sin romper nada.

## Proyecto

EntreVecinos es un tablón de anuncios privado por comunidades de vecinos: registro con validación del correo, comunidades con solicitud de acceso, anuncios con fotografías, búsqueda, filtros, contacto y moderación. El producto, la documentación y las especificaciones están en español de España.

| Ruta | Contenido |
|---|---|
| `apps/api/` | API REST: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PyJWT, boto3; dependencias con uv |
| `apps/web/` | Web: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, zod |
| `infra/` | Docker Compose: `db` (PostgreSQL 16), `storage` (MinIO), `mail` (Mailpit), `api`, `web` |
| `docs/api/openapi.yaml` | Contrato de referencia de la API |
| `docs/product/` | Historias de usuario (`user-stories.md`) y tickets (`tickets/`) |
| `openspec/` | Especificaciones vigentes (`specs/`) y cambios (`changes/`, `changes/archive/`) |

## Entorno y comandos

Todo se ejecuta en contenedores: no instales Python, Node ni dependencias en el host. Desde la raíz, con `.env` creado a partir de `.env.example`:

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"

make dev              # construye, levanta db, mail, api y web y aplica las migraciones
make build-backend    # reconstruye la API (necesario tras cambiar dependencias o tests)
make build-frontend   # reconstruye la web
make migrate          # aplica las migraciones pendientes
```

Verificación antes de dar un cambio por terminado:

```bash
# API (las pruebas se copian en la imagen; el volumen evita reconstruir)
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check .
$COMPOSE run --rm api ruff format --check .

# Web
$COMPOSE exec web npm run lint
$COMPOSE exec web npm run typecheck
$COMPOSE exec web npm run test
```

- Ejecuta solo las pruebas afectadas mientras iteras (`pytest tests/test_x.py`, `npm run test -- <ruta>`) y la suite completa al final.
- Las pruebas `@pytest.mark.db` usan la base `<POSTGRES_DB>_test`, que se crea y migra sola; nunca tocan la de desarrollo.
- Servicios locales: web http://localhost:3000, API http://localhost:8000/docs, correo http://localhost:8025.

## Arquitectura

### API (`apps/api/src/entrevecinos/`): arquitectura limpia

```
domain/          entidades, errores y reglas; sin frameworks ni otras capas
application/     casos de uso (clases con execute()) y puertos; solo depende de domain
infrastructure/  adaptadores: repositorios SQLAlchemy, S3, correo, seguridad, settings
presentation/    FastAPI: create_app() y routers versionados en v1/
```

`tests/test_architecture.py` hace cumplir estas dependencias. Cada área funcional (`users`, `communities`, `listings`, `media`…) tiene su subpaquete en cada capa que necesita.

Usa siempre los puntos únicos existentes; no repliques su lógica:

- Permisos por comunidad: `CommunityAccess.require_member` / `require_role` (inyectado con `CommunityAccessDep`). Ningún endpoint compara roles por su cuenta.
- Visibilidad de un anuncio: `ListingVisibility`. Lecturas de anuncios: `ListingLoader` (evita N+1).
- Usuario autenticado: `CurrentUserDep`. Paginación: `PageParams` / `Page[T]`, y `PageRequest` / `PageResult[T]` en aplicación.
- «No encontrado»: hereda de `domain.errors.NotFoundError` (→ `404`).

### Web (`apps/web/src/`)

```
app/          rutas y layouts; zona privada en app/(privado)/
features/     código por funcionalidad: componentes, Server Actions y lógica
components/   componentes compartidos (ui/)
lib/          utilidades y cliente de la API
styles/       globals.css: tema (@theme), paletas y estilos base
```

- Next.js 16 rompe APIs anteriores: lee `apps/web/AGENTS.md` y la guía correspondiente de `node_modules/next/dist/docs/` antes de escribir código de Next.
- El navegador nunca recibe el JWT: las Server Actions y las páginas de servidor llaman a la API con `apiFetch` / `userApiFetch` (`server-only`) y la sesión vive en la cookie `HttpOnly` `ev_session`.
- Cada página y Server Action privadas llaman a `requireUser()`; el *layout* no protege nada.
- Los ficheros `"use server"` solo exportan funciones `async`.
- Extrae a `components/` o `lib/` solo lo que tenga más de un uso.

## Convenciones

- **Idioma:** textos de la interfaz, documentación, specs, tickets y comentarios en español; identificadores del código en inglés.
- **Estilo:** imita el código de alrededor (nombres, densidad de comentarios, estructura). Python: ruff, línea de 100. TypeScript: ESLint de Next y alias `@/*`.
- **Pruebas:** todo cambio de comportamiento lleva pruebas. API en `apps/api/tests/`; web junto al código (`*.test.ts(x)`).
- **Contrato:** si cambia una petición o respuesta de la API, actualiza `docs/api/openapi.yaml`.
- **Esquema:** cualquier cambio de modelo lleva una migración Alembic revisada a mano, con `downgrade()`.
- **Dependencias:** se añaden con uv o npm dentro de contenedores (ver los README de cada app) y se versionan los *lockfiles*.
- **Commits:** en inglés, [Conventional Commits](https://www.conventionalcommits.org/) (`feat`, `fix`, `docs`, `refactor`…, ámbito opcional); asunto en imperativo y cuerpo que explique el porqué.

## Flujo de trabajo: tickets y OpenSpec

1. Cada funcionalidad parte de una historia (`HU-xx`) de `docs/product/user-stories.md` y de sus tickets en `docs/product/tickets/EP-xx-…/HU-xx-…/TK-yyy-<capa>-<descripcion>.md` (convenciones en `docs/product/tickets/README.md`).
2. Cada ticket se implementa como un change de OpenSpec llamado `tk-yyy-<capa>-<descripcion>` (`/opsx:propose`, `/opsx:apply`, `/opsx:archive`). El contexto y las reglas de los artefactos están en `openspec/config.yaml`.
3. Al archivar, las *delta specs* se sincronizan con `openspec/specs/`. No edites esas specs sin un change que lo justifique.

## Seguridad y límites

- Nunca subas `.env` ni secretos; documenta las variables nuevas en `.env.example` con valores ficticios.
- La autorización se decide en la API. Ocultar un botón en la web no protege nada.
- No relajes la `Content-Security-Policy` (con *nonce*, en `apps/web/src/proxy.ts`) ni las cabeceras de seguridad de `apps/web/next.config.ts` sin motivo explícito.
- Las imágenes se validan por contenido (*magic bytes*) y tamaño; se leen siempre con URL prefirmada, nunca con un bucket público.
- Pide confirmación antes de acciones difíciles de deshacer: borrar volúmenes (`docker compose down -v`), reescribir historia publicada (`push --force`) o modificar migraciones ya aplicadas.
