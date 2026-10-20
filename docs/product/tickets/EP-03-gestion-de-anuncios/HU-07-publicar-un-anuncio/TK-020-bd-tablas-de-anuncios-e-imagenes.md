# TK-020 · Base de datos: categorías, anuncios e imágenes

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos |
| **Componente** | `apps/api/` (`infrastructure/db/models/`, `migrations/`) |
| **Historia** | HU-07 Publicar un anuncio (Épica 3) |
| **Prioridad** | Alta (bloquea las Épicas 3, 4 y 5) |
| **Depende de** | TK-012, TK-015 (migración `0003`) |
| **Referencias** | `readme.md` §3.2 (`category`, `listing`, `media_asset`, `listing_image`; enums `listing_type` y `listing_status`; índices recomendados) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Publicar un anuncio requiere categorías, el propio anuncio y sus imágenes. El modelo de datos los define, pero no existen en la base de datos.

**Objetivo:** crear la migración `0004` con los enums `listing_type` y `listing_status`, las tablas `category`, `listing`, `media_asset` y `listing_image`, los índices recomendados y las categorías iniciales.

## 2. Alcance

**Incluye**
- Modelos ORM y migración reversible.
- Datos iniciales de categorías (en la propia migración).
- Restricciones de precio y moneda, y de portada única.
- Pruebas de restricciones.

**No incluye**
- Índice de búsqueda de texto completo: lo añade TK-030 junto con la búsqueda.
- Tablas posteriores al MVP (conversaciones, denuncias…).
- La FK `users.avatar_asset_id → media_asset.id` sí se añade aquí, ahora que existe la tabla (pendiente desde TK-005).

## 3. Requisitos técnicos

### 3.1 Enums

- `listing_type`: `sell`, `wanted`, `offer_service`, `need_service`, `free`, `other`.
- `listing_status`: `draft`, `active`, `reserved`, `completed`, `hidden`, `deleted` (todos los del modelo; la API solo expone algunos).

### 3.2 `category`

`id` UUID PK · `name VARCHAR(80)` `NOT NULL UNIQUE` · `slug VARCHAR(100)` `NOT NULL UNIQUE`, `CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$')` · `is_active BOOLEAN NOT NULL DEFAULT true`.

Categorías iniciales (asumido, revisables por negocio): Hogar y jardín · Electrónica · Moda y complementos · Infantil · Deporte y ocio · Libros y música · Motor · Servicios · Mascotas · Otros.

### 3.3 `listing`

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `UUID` | PK |
| `community_id` | `UUID` | `NOT NULL`, FK → `community.id` |
| `owner_id` | `UUID` | `NOT NULL`, FK → `users.id` |
| `category_id` | `UUID` | `NOT NULL`, FK → `category.id` |
| `title` | `VARCHAR(160)` | `NOT NULL`, `CHECK (length(trim(title)) > 0)` |
| `description` | `TEXT` | `NOT NULL`, `CHECK (length(trim(description)) > 0)` |
| `type` | `listing_type` | `NOT NULL` |
| `price` | `NUMERIC(10,2)` | `NULL`, `CHECK (price IS NULL OR price >= 0)` |
| `currency` | `CHAR(3)` | `NULL`, `CHECK (currency ~ '^[A-Z]{3}$')` |
| `status` | `listing_status` | `NOT NULL`, `DEFAULT 'active'` |
| `published_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` |
| `created_at`, `updated_at` | `TIMESTAMPTZ` | `NOT NULL`; `updated_at` con `onupdate=statement_timestamp()` |
| `deleted_at` | `TIMESTAMPTZ` | `NULL` |

- `CHECK ((price IS NULL) = (currency IS NULL))`: hay moneda si y solo si hay precio (asumido: el README dice «exigir moneda cuando hay precio»; tampoco tiene sentido una moneda sin precio).
- Índices del README: `(community_id, status, published_at DESC)`, `(community_id, type, published_at DESC)`, `(category_id, published_at DESC)`, `(price)`, y además `(owner_id)` para «mis anuncios».
- Las FK usan `ON DELETE RESTRICT`: el borrado es lógico.

### 3.4 `media_asset`

`id` UUID PK · `uploaded_by UUID NOT NULL` FK → `users.id` · `object_key VARCHAR(512) NOT NULL UNIQUE` · `mime_type VARCHAR(100) NOT NULL`, `CHECK (mime_type IN ('image/jpeg','image/png','image/webp'))` · `size_bytes BIGINT NOT NULL CHECK (size_bytes > 0)` · `sha256 CHAR(64) NULL` · `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`. Índice `(uploaded_by)`.

### 3.5 `listing_image`

`listing_id` (PK compuesta, FK → `listing.id` `ON DELETE CASCADE`) · `asset_id` (PK compuesta, FK → `media_asset.id` `ON DELETE RESTRICT`) · `position SMALLINT NOT NULL DEFAULT 0 CHECK (position >= 0)` · `is_cover BOOLEAN NOT NULL DEFAULT false`.

- Índice `(asset_id)` (README) e índice único parcial `UNIQUE (listing_id) WHERE is_cover` (como máximo una portada por anuncio, `ListingImagesUpdate`).
- `UNIQUE (listing_id, position)` para un orden sin empates (asumido).

### 3.6 Pruebas (`@pytest.mark.db`)

- Categorías iniciales presentes tras la migración.
- Precio negativo, precio sin moneda y moneda sin precio rechazados; anuncio sin precio aceptado.
- Título o descripción en blanco rechazados.
- Dos portadas en el mismo anuncio rechazadas.
- `alembic check` y migraciones reversibles.

## 4. Criterios de aceptación

**AC1 — Migración aplicada**
- **Given** `make dev`
- **When** consulto las tablas y `select name from category`
- **Then** existen con las restricciones e índices de §3 y las diez categorías iniciales

**AC2 — Coherencia del precio**
- **Given** la tabla `listing`
- **When** inserto un anuncio con `price = -1`, con precio y sin moneda, o con moneda y sin precio
- **Then** la base de datos lo rechaza; sin precio ni moneda lo acepta

**AC3 — Portada única**
- **Given** un anuncio con una imagen de portada
- **When** marco otra como portada
- **Then** la base de datos lo rechaza

**AC4 — Reversible**
- **Given** la base de datos en `0004`
- **When** ejecuto `alembic downgrade 0003` y `upgrade head`
- **Then** ambos terminan sin errores

## 5. Plan de tareas

1. Modelos ORM.
2. Migración `0004` (enums, tablas, índices, FK del avatar, datos iniciales).
3. Pruebas de §3.6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec db psql -U entrevecinos -c '\d listing' -c 'select name, slug from category'
$COMPOSE run --rm api alembic downgrade 0003 && $COMPOSE run --rm api alembic upgrade head
$COMPOSE run --rm api alembic check && $COMPOSE run --rm api pytest -m db
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `pytest`, `ruff check` y `alembic check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Categorías iniciales:** propuesta; la gestión por `platform_admin` (`POST/PATCH /categories`) no tiene historia en el MVP.
- **`published_at`:** igual a la creación mientras no haya borradores (`draft` no se usa en el MVP).
