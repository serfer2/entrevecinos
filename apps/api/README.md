# API de EntreVecinos

Backend en Python con FastAPI, organizado con arquitectura limpia. Las dependencias se gestionan con [uv](https://docs.astral.sh/uv/) dentro del contenedor, así que no hace falta instalar Python ni uv en el host.

## Estructura

```
src/entrevecinos/
├── domain/          # entidades y reglas de negocio, sin dependencias de framework
├── application/     # casos de uso y puertos; solo depende de domain
├── infrastructure/  # adaptadores (configuración, base de datos, ficheros…)
└── presentation/    # FastAPI: create_app() y routers versionados (v1/)
```

Reglas de dependencias (comprobadas por `tests/test_architecture.py`):

- `domain` no importa frameworks (`fastapi`, `starlette`, `pydantic_settings`, `uvicorn`, `sqlalchemy`, `boto3`…) ni otras capas.
- `application` solo depende de `domain`.
- `infrastructure` y `presentation` pueden depender de `application` y `domain`.

## Ejecutar

Desde la raíz del repositorio (con `.env` creado a partir de `.env.example`):

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE up -d --build api      # levanta db y api; recarga automática al editar src/
```

- Documentación interactiva: http://localhost:8000/docs
- Especificación de referencia de la API: `docs/api/openapi.yaml`

## Base de datos y migraciones

Persistencia con SQLAlchemy 2 (síncrono) y psycopg 3; esquema versionado con Alembic en `migrations/`.

- Modelos ORM: `src/entrevecinos/infrastructure/db/models/` (registrarlos en `models/__init__.py`).
- Sesión por petición: dependencia `get_session()` de `infrastructure/db/session.py` (commit al terminar, rollback si hay error).
- La tabla de usuarios se llama `users` (`user` es palabra reservada en PostgreSQL).

```bash
make migrate                                                  # aplica las migraciones pendientes
$COMPOSE run --rm api alembic current                         # versión actual
$COMPOSE run --rm -v "$PWD/apps/api/migrations:/app/migrations" api \
  alembic revision --autogenerate -m "descripcion"            # nueva migración (revísala siempre)
$COMPOSE run --rm api alembic downgrade -1                    # revertir la última
$COMPOSE run --rm api alembic check                           # el modelo y las migraciones coinciden
```

`make dev` aplica las migraciones al levantar el entorno. Cada migración debe incluir `downgrade()`.

### Pruebas con base de datos

Las pruebas marcadas con `@pytest.mark.db` usan la base de datos `<POSTGRES_DB>_test`, que la fixture `db_engine` crea y migra automáticamente. Cada prueba recibe `db_session`, dentro de una transacción que se revierte al terminar: la base de datos de desarrollo nunca se modifica.

```bash
$COMPOSE run --rm api pytest -m db        # solo integración
$COMPOSE run --rm api pytest -m "not db"  # sin base de datos
```

Las pruebas se copian en la imagen: tras cambiarlas, `make build-backend`.

## Configuración

| Variable | Uso | Valor por defecto |
|---|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL (`postgresql+psycopg://…`) | obligatoria |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas | `http://localhost:3000` |
| `ENVIRONMENT` | `development` o `production` | `development` |
| `JWT_SECRET` | Clave de firma de los JWT (HS256, mínimo 32 caracteres) | obligatoria |
| `JWT_TTL_SECONDS` | Duración del token de acceso en segundos | `86400` |
| `STORAGE_ENDPOINT` | Endpoint S3 para subir (red interna) | obligatoria |
| `STORAGE_PUBLIC_ENDPOINT` | Endpoint S3 con el que se firman las URL que abre el navegador | obligatoria |
| `STORAGE_BUCKET` | Bucket privado de las imágenes | obligatoria |
| `STORAGE_ACCESS_KEY` / `STORAGE_SECRET_KEY` | Credenciales S3 propias de la API | obligatorias |
| `MEDIA_MAX_BYTES` | Tamaño máximo de una imagen | `5242880` (5 MB) |
| `MEDIA_URL_TTL_SECONDS` | Validez de las URL prefirmadas | `300` |
| `SMTP_HOST` | Servidor SMTP (`mail` en desarrollo) | obligatoria |
| `SMTP_PORT` | Puerto SMTP | `587` (`1025` en `.env.example`) |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | Credenciales SMTP | vacías |
| `SMTP_STARTTLS` | STARTTLS; en producción debe ser `true` | `true` |
| `MAIL_FROM` | Remitente de los correos | obligatoria |
| `WEB_PUBLIC_URL` | Origen de los enlaces que se envían por correo; en producción, `https` | obligatoria |
| `EMAIL_VERIFICATION_TTL_HOURS` | Caducidad del enlace de validación del correo (`> 0`) | `24` |

## Salud

`GET /v1/health` (público) responde `{"status": "ok"}` si la API llega a la base de datos y `503` si no. Lo usa el healthcheck de Compose.

## Autenticación

- `POST /v1/auth/register` crea la cuenta **inactiva**, sin validar el correo, y responde `RegistrationResponse` (`email`, `verification_expires_at`), sin JWT. El correo con el enlace `{WEB_PUBLIC_URL}/verificar-correo?token=…` se envía tras responder (`BackgroundTasks`): si el SMTP falla, la cuenta queda creada y el error va al log. Un correo ya registrado → `409` con `code: email_in_use`, o `email_pending_verification` si la cuenta está pendiente (no se modifica).
- `POST /v1/auth/email-verification` (público) valida el token: activa la cuenta y devuelve `AuthResponse`. Caducado → `410` `verification_expired` con el `email`; desconocido, usado o sustituido → `400` `verification_invalid`.
- `POST /v1/auth/email-verification/resend` (público) responde siempre `202`; si la cuenta está pendiente y su último enlace tiene al menos 60 segundos, crea otro y lo envía.
- Tokens de validación: `secrets.token_urlsafe(32)`, guardados como SHA-256 en `email_verification`; emitir uno borra los anteriores del usuario (`EmailVerificationIssuer`, `application/users/email_verification.py`).
- `POST /v1/auth/token` inicia sesión. Ante cualquier fallo responde `401` con el mismo mensaje (`Correo o contraseña incorrectos.`) y el mismo coste de verificación, exista o no la cuenta. Con la contraseña correcta y el correo sin validar (salvo `platform_admin`) → `403` `email_not_verified`.
- Envío de correo: puerto `EmailSender` (`application/users/ports.py`) y adaptador `SmtpEmailSender` (`infrastructure/mail/`, `smtplib`). En desarrollo llega a Mailpit: http://localhost:8025.
- `GET /v1/users/me` devuelve el usuario autenticado.
- `PATCH /v1/users/me` actualiza parcialmente `full_name` y `phone` (`null` o `""` borra el teléfono). `avatar_asset_id`, `password` y `current_password` del contrato aún no están implementados y se rechazan con `422`.
- Contraseñas con Argon2id (`pwdlib`); tokens HS256 (`pyjwt`) con `sub`, `iat` y `exp`. El algoritmo está fijado en código.
- Los errores `422` solo devuelven `loc`, `msg` y `type` (nunca los valores enviados).
- Los errores de dominio se traducen a HTTP en `presentation/errors.py`.
- En las pruebas, la fixture `email_sender` sustituye el SMTP por `FakeEmailSender` (`tests/fakes.py`), que guarda los correos en `sent`; `last_token(correo)` devuelve el token del último enlace. El *helper* `register` (`tests/api_helpers.py`) registra **y valida** la cuenta, para que las pruebas trabajen con cuentas activas; `register_pending` la deja sin validar.

## Comunidades

- `POST /v1/communities` crea la comunidad; el creador queda como `community_admin` con membresía `approved` (misma transacción).
- `GET /v1/communities/{community_id}` devuelve una comunidad activa a cualquier usuario autenticado.

- `GET /v1/communities` busca comunidades activas: `q` (nombre o descripción), `city` y `postal_code` (prefijo), sin distinguir mayúsculas ni tildes (`f_unaccent`, migración `0003`; helpers en `infrastructure/db/text_search.py`).
- `POST /v1/communities/{id}/memberships` crea una solicitud `pending`. Si ya existe una membresía en cualquier estado responde `409 {"detail": …, "status": "<estado>"}`.
- `GET /v1/users/me/memberships` lista las membresías propias con la comunidad embebida (filtro `status`).

- `GET /v1/communities/{id}/memberships` (gestores: `community_admin`, `moderator`, `platform_admin`) y `PATCH /v1/communities/{id}/memberships/{user_id}` (`community_admin`, `platform_admin`) revisan las solicitudes: solo `pending → approved | rejected`; otra transición → `409`.

- Gestión de miembros (`ChangeMembershipStatus`, `RemoveMembership`): bloquear (`approved → blocked`) y desbloquear (`blocked → approved`, conserva `joined_at`); no se puede bloquear a un administrador ni a uno mismo (`409`). `DELETE …/memberships/{user_id}` expulsa (o sale, si es la propia); nunca deja la comunidad sin administrador (`409`). El bloqueado no puede volver a solicitar el acceso; el expulsado sí.
- Los anuncios de autores sin membresía aprobada (bloqueados o expulsados) no se muestran: `OWNER_IS_MEMBER` en el filtro del listado y `Listing.owner_is_member` en `ListingVisibility` (solo los ven el autor y los gestores). Se calcula al consultar, sin cambiar el estado del anuncio.

## Autorización por comunidad

Todas las comprobaciones de permisos por comunidad pasan por `CommunityAccess` (`application/authorization/community_access.py`); ningún endpoint compara roles por su cuenta.

- `require_member(user, community_id)`: exige membresía `approved`. Sin membresía → `PermissionDenied` (`403`); con membresía no aprobada → `MembershipNotApproved` (`403` con `status`, `MembershipForbidden` en el contrato).
- `require_role(user, community_id, roles)`: además, uno de `roles` (`COMMUNITY_ADMINS`, `COMMUNITY_MANAGERS`). Sin permisos → `403` sin `status`.
- Ambos responden antes `404` si la comunidad no existe y dejan pasar siempre a `platform_admin`.

```python
from entrevecinos.application.authorization.community_access import COMMUNITY_ADMINS

class DoSomething:
    def __init__(self, access: CommunityAccess, ...): ...

    def execute(self, user: User, community_id: uuid.UUID) -> ...:
        self._access.require_role(user, community_id, COMMUNITY_ADMINS)
        ...
```

En los routers, la política se inyecta con `CommunityAccessDep`.

## Anuncios

- `GET /v1/categories`: categorías activas («Otros» al final).
- `POST /v1/communities/{id}/listings`: solo miembros aprobados (`require_member`). Hasta 10 imágenes propias no usadas en otro anuncio (la primera es la portada); con precio y sin moneda se usa `EUR`; moneda sin precio → `422`.
- `Listing` incluye `owner` (leído siempre de `users`) e `images` ordenadas. Los precios son `Decimal` de extremo a extremo y se serializan como número JSON.
- `PATCH /v1/listings/{id}` (parcial; `UNSET` de `application/unset.py` distingue «no enviado» de `null`) y `PUT /v1/listings/{id}/images` (sustituye el conjunto): solo el autor con membresía aprobada; un anuncio retirado responde `403` (`ListingLocked`). La regla común está en `EditableListing`.
- `PATCH /v1/listings/{id}/status` (`ChangeListingStatus`): el autor reserva (`active ↔ reserved`) y finaliza (`→ completed`, estado final que bloquea la edición); la gestión de la comunidad retira (`hidden`, registra `hidden_by`/`hidden_at`, migración `0006`) y restaura (`active`). `active` se interpreta según el estado actual. Reservar o finalizar el anuncio de otro → `403`; transición no permitida → `409`.
- `DELETE /v1/listings/{id}`: borrado lógico (`deleted_at`, `status = deleted`) por el autor, un gestor de la comunidad o `platform_admin`. Las lecturas parten de `listing_with_owner()`, que ya excluye los eliminados.
- `GET /v1/communities/{id}/listings`: anuncios `active` y `reserved` de la comunidad para miembros aprobados, del más reciente al más antiguo (`published_at DESC, id DESC`). Los criterios llegan en `ListingQuery`; el filtro de visibilidad común está en `SqlAlchemyListingRepository._visible_in_community` (lo comparten la página y el `total`).
- Búsqueda (`q`): texto completo de PostgreSQL con la configuración `es_unaccent` (español sin tildes, migración `0005`) sobre la columna generada `listing.search_vector` (índice GIN). `prefix_tsquery()` (`domain/listings/search.py`) convierte la búsqueda en prefijos combinados con `AND` y descarta todo lo que no sean palabras. Vacío = sin búsqueda; 1 carácter → `422`.
- `GET /v1/listings/{id}`: detalle. La visibilidad de un anuncio la decide solo `ListingVisibility` (`application/listings/visibility.py`): membresía aprobada (403) y, si está `hidden` o `draft`, solo autor y gestores (404 para el resto). La usan el detalle, las imágenes y la edición.
- Los anuncios de cuentas eliminadas no aparecen en ninguna lectura.
- `ListingLoader` (`infrastructure/listings/sqlalchemy_listing_repository.py`) carga anuncios con su autor y todas sus imágenes en dos consultas: úsalo en cualquier lectura de anuncios para evitar N+1.

## Imágenes

- `POST /v1/media` (multipart, campo `file`) guarda una imagen en el almacenamiento de objetos. El tipo se decide por los *magic bytes* (JPEG, PNG o WebP; otro → `415`), máximo `MEDIA_MAX_BYTES` (→ `413`, comprobado antes de leer el cuerpo cuando hay `Content-Length`); vacío → `422`. La clave del objeto es `media/<usuario>/<uuid>.<ext>`.
- `GET /v1/media/{id}` responde `302` a una URL prefirmada (`MEDIA_URL_TTL_SECONDS`) si el usuario la subió o puede ver (`ListingVisibility`) el anuncio que la usa; si no, `403`.
- `S3ObjectStorage` sube por `STORAGE_ENDPOINT` y firma con `STORAGE_PUBLIC_ENDPOINT`, porque la firma incluye el host que abre el navegador.
- En las pruebas, la fixture `object_storage` sustituye el almacenamiento por uno en memoria; `pytest -m storage` prueba contra el MinIO real.

## Paginación

Todos los listados paginados usan `PageParams` (`page ≥ 1`, por defecto 1; `page_size` de 1 a 100, por defecto 20) y responden `Page[T]` (`items`, `page`, `page_size`, `total`), definidos en `presentation/v1/pagination.py`. En aplicación, los repositorios reciben `PageRequest` y devuelven `PageResult[T]` (`application/pagination.py`). Una página posterior a la última devuelve `items: []` con el `total` real.

```python
@router.get("")
def list_things(page: PageParams, ...) -> Page[ThingResponse]:
    result = ListThings(repo).execute(page)
    return Page.build(result, page, [ThingResponse.from_domain(t) for t in result.items])
```

## Errores comunes

- Los errores «no encontrado» de cualquier área heredan de `domain.errors.NotFoundError` y responden `404 {"detail": "Recurso no encontrado."}`.
- Textos de entrada: `RequiredText(n)` y `OptionalText(n)` (`presentation/v1/schemas/common.py`) recortan espacios; en los opcionales `""` equivale a `null`.

### Proteger un endpoint

Usa siempre la dependencia `CurrentUserDep` (`presentation/dependencies.py`); valida el token (firma, `exp`, algoritmo HS256) y que el usuario siga activo y no eliminado. Si falla, responde `401` con `WWW-Authenticate: Bearer`:

```python
from entrevecinos.presentation.dependencies import CurrentUserDep


@router.get("/algo", responses=UNAUTHORIZED)
def algo(user: CurrentUserDep) -> ...: ...
```

## Pruebas y lint

```bash
$COMPOSE run --rm api pytest
$COMPOSE run --rm api ruff check .
$COMPOSE run --rm api ruff format --check .
```

## Dependencias

Se usa la imagen oficial de uv para modificar `pyproject.toml` y `uv.lock` sin instalar nada en el host (desde `apps/api/`):

```bash
UV="docker run --rm -u $(id -u):$(id -g) -e UV_CACHE_DIR=/tmp/uv-cache -v $PWD:/app -w /app --entrypoint uv ghcr.io/astral-sh/uv:0.13.1-python3.12-trixie-slim"
$UV add <paquete>          # runtime
$UV add --dev <paquete>    # desarrollo
$UV lock                   # regenerar el lock
```

Después, reconstruye la imagen (`$COMPOSE build api`). `pyproject.toml` y `uv.lock` se versionan.

## Añadir un módulo funcional

Cada área (usuarios, comunidades, anuncios…) crea su subpaquete en cada capa que necesite:

```
domain/listings/            # entidades y errores de dominio
application/listings/       # casos de uso y puertos (interfaces de repositorio)
infrastructure/listings/    # implementaciones de los puertos
presentation/v1/listings.py # router FastAPI, incluido desde presentation/v1/router.py
```

## Imagen de producción

```bash
docker build --target prod -t entrevecinos-api:prod apps/api
```

Solo instala dependencias de runtime, sin `--reload` y con usuario no root.
