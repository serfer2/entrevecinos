# TK-022 · Backend: categorías y publicar un anuncio (`GET /v1/categories`, `POST /v1/communities/{id}/listings`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (áreas `categories` y `listings`) |
| **Historia** | HU-07 Publicar un anuncio (Épica 3) |
| **Prioridad** | Alta |
| **Depende de** | TK-017, TK-020, TK-021 |
| **Referencias** | `docs/api/paths/categories.yaml` (`get`), `communities_community_id_listings.yaml` (`post`); esquemas `Category`, `ListingCreate`, `Listing`, `ListingOwner`, `ListingImage`, `ListingType` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-07 pide que un miembro aprobado publique un anuncio con título, descripción, categoría, tipo, precio opcional y fotografías, y que nadie sin acceso aprobado pueda hacerlo.

**Objetivo:** implementar el listado de categorías activas y la publicación de anuncios con sus imágenes, y la representación `Listing` que usarán el resto de endpoints de anuncios.

## 2. Alcance

**Incluye**
- `GET /v1/categories`.
- `POST /v1/communities/{id}/listings`, con `image_asset_ids` (máximo 10; el primero es la portada).
- Dominio `listings` y `ListingResponse` (incluye `owner` e `images`).

**No incluye**
- Gestión de categorías por `platform_admin` (sin historia).
- Listado, búsqueda y detalle (Épicas 4 y 5), edición (TK-024), borrado (TK-026), estados (TK-042).

## 3. Requisitos técnicos

### 3.1 `GET /v1/categories` (autenticado)

- **200** `{items: Category[]}` solo con `is_active = true`, ordenadas por `name` (con «Otros» al final, asumido).

### 3.2 `POST /v1/communities/{community_id}/listings`

- Autorización: `CommunityAccess.require_member` (TK-017): **403** si no es miembro aprobado (con `status` si la membresía existe, para el aviso de «pendiente»).
- **Petición** (`ListingCreate`, `extra="forbid"`):
  - `category_id`: UUID de una categoría **activa** → si no, **422** con `loc` `["body", "category_id"]`.
  - `title`: se recorta; 1–160. `description`: se recorta; 1–5000 (asumido: el contrato no acota; conviene añadirlo).
  - `type`: `ListingType`.
  - `price`: `null` o `0 ≤ price ≤ 99 999 999.99`, con dos decimales como máximo (`Decimal`, nunca `float`).
  - `currency`: `^[A-Z]{3}$`. Si hay precio y no hay moneda, se usa `EUR` (asumido: el MVP es local y en euros; el contrato dice «requerido si se indica precio», así que se propone documentar el valor por defecto). Moneda sin precio → **422**.
  - `image_asset_ids`: 0–10 UUID distintos, todos subidos por el usuario (`uploaded_by`) y no asociados a otro anuncio (asumido) → si no, **400** `{"detail": "Alguna imagen no es válida."}`.
- Efecto: crea el anuncio (`status = active`, `published_at = now()`) y sus `listing_image` en orden (`position = índice`, `is_cover = índice 0`), en una transacción.
- **201** `Listing`.

### 3.3 Representación `Listing`

- `owner`: `ListingOwner` con `id`, `full_name`, `phone` y `avatar_url` (`null` por ahora). El teléfono se incluye porque toda respuesta `Listing` se entrega solo a miembros aprobados (contrato; TK-038 añade el correo).
- `images`: `ListingImage[]` (`asset_id`, `url: "/v1/media/<asset_id>"`, `position`, `is_cover`) ordenadas por `position`.
- `price`: se serializa como número JSON con dos decimales; `null` si no hay.
- Los datos del anunciante se leen siempre de `users` (no se copian), para que los cambios de perfil se reflejen (TK-010 §3.3).

### 3.4 Diseño por capas

- `domain/listings/`: `Listing`, `NewListing`, `ListingType`, `ListingStatus`, `Money`/validación de precio, errores `InvalidCategory`, `InvalidImages`.
- `application/listings/`: `PublishListing`; puertos `ListingRepository`, `CategoryRepository`, `MediaRepository` (de TK-021, con `owned_unattached(ids, user_id)`).
- Lectura de un anuncio con propietario e imágenes en una sola consulta (sin N+1), reutilizable por TK-028 y TK-036.

### 3.5 Pruebas

- Unitarias de `PublishListing` (precio por defecto en EUR, imágenes válidas e inválidas, categoría inactiva).
- Integración: publicación con y sin precio, con 0, 1 y 10 imágenes (portada = primera), 11 imágenes (**422**), imagen ajena (**400**), categoría inexistente o inactiva (**422**), campos vacíos (**422** por campo), miembro pendiente (**403** con `status: "pending"`), ajeno (**403**), sin token (**401**).

## 4. Criterios de aceptación

**AC1 — Publicación correcta (HU-07 AC1)**
- **Given** que soy miembro aprobado de una comunidad
- **When** publico con título, descripción, categoría y tipo `sell`
- **Then** recibo `201` con `status: "active"`, `published_at` actual y `owner` con mi nombre

**AC2 — Precio opcional (HU-07 AC2)**
- **Given** que publico un anuncio `free` sin precio
- **When** consulto la respuesta
- **Then** `price` y `currency` son `null`; con `price: 45` sin moneda, `currency` es `EUR`

**AC3 — Fotografías (HU-07 AC3)**
- **Given** tres imágenes subidas por mí con `POST /v1/media`
- **When** publico con sus ids
- **Then** `images` tiene tres elementos en ese orden, el primero con `is_cover: true`, y cada `url` responde `302` para los miembros de la comunidad

**AC4 — Campos obligatorios (HU-07 AC4)**
- **Given** que soy miembro aprobado
- **When** publico sin título, descripción, categoría o tipo
- **Then** recibo `422` con un error por cada campo que falta y no se crea el anuncio

**AC5 — Sin acceso aprobado (HU-07 AC5)**
- **Given** que mi membresía está pendiente o no pertenezco a la comunidad
- **When** intento publicar
- **Then** recibo `403` y no se crea el anuncio

## 5. Plan de tareas

1. `GET /v1/categories`.
2. Dominio y caso de uso `PublishListing` con pruebas unitarias.
3. Repositorio (anuncio + imágenes en una transacción; lectura con propietario e imágenes).
4. Endpoint y `ListingResponse`; comprobar el contrato en `/openapi.json`.
5. Pruebas de integración y verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s http://localhost:8000/v1/categories -H "Authorization: Bearer $TOKEN"
curl -s -X POST http://localhost:8000/v1/communities/<id>/listings -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"category_id":"<cat>","title":"Bicicleta infantil","description":"Poco uso","type":"sell","price":45,"image_asset_ids":["<asset>"]}'
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] Los precios se tratan como `Decimal` de extremo a extremo.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Moneda por defecto `EUR` y límite de `description`:** propuestas de cambio del contrato.
- **Reutilizar una imagen en varios anuncios:** se prohíbe para simplificar permisos y borrado.
