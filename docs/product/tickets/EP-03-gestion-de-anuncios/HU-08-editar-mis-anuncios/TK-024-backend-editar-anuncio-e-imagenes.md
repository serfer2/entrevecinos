# TK-024 · Backend: editar un anuncio propio y sus imágenes

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `listings`) |
| **Historia** | HU-08 Editar mis anuncios (Épica 3) |
| **Prioridad** | Media |
| **Depende de** | TK-022 |
| **Referencias** | `docs/api/paths/listings_listing_id.yaml` (`patch`), `listings_listing_id_images.yaml` (`put`); esquemas `ListingUpdate`, `ListingImagesUpdate`, `Listing` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-08 pide que el autor modifique título, descripción, categoría, tipo, precio o fotografías, que no se pueda dejar vacío el título ni la descripción, y que solo el autor pueda editar.

**Objetivo:** implementar `PATCH /v1/listings/{id}` (actualización parcial) y `PUT /v1/listings/{id}/images` (sustitución del conjunto de imágenes), ambos solo para el autor.

## 2. Alcance

**Incluye**
- Casos de uso `UpdateListing` y `ReplaceListingImages`.
- Regla común «anuncio editable por el usuario» (autor, anuncio no eliminado).

**No incluye**
- Cambios de estado (`PATCH /listings/{id}/status`): moderación en TK-042, reservar y finalizar en TK-044. TK-044 añade aquí que un anuncio `completed` no se puede editar (**403**).
- Edición por administradores: el contrato solo permite al autor.

## 3. Requisitos técnicos

### 3.1 Acceso común

- Anuncio inexistente o eliminado (`deleted_at`) → **404**.
- El usuario no es el autor → **403**. Se comprueba además que sigue siendo miembro aprobado de la comunidad (un autor expulsado o bloqueado no puede editar, asumido) → **403**.
- Anuncio `hidden` (retirado por un administrador): el autor **no** puede editarlo → **403** `{"detail": "Este anuncio ha sido retirado por la administración de la comunidad."}` (asumido: evita «republicarlo» editándolo).

### 3.2 `PATCH /v1/listings/{listing_id}`

- `ListingUpdate` (`extra="forbid"`, al menos un campo): `category_id` (activa), `title`, `description`, `type`, `price`, `currency`, con las mismas reglas que la creación (TK-022 §3.2). `title` y `description` no admiten `null` ni texto en blanco (patrón «no enviado» frente a `null` de TK-010).
- Coherencia del precio sobre el **resultado** de aplicar los cambios: `{"price": null}` borra también la moneda; `{"price": 40}` sin moneda conserva la actual o usa `EUR`; `{"currency": "USD"}` sin precio existente → **422**.
- No modifica `published_at` (asumido: editar no «sube» el anuncio en el listado).
- **200** `Listing`. Ante cualquier error no se modifica nada (HU-08 AC2).

### 3.3 `PUT /v1/listings/{listing_id}/images`

- `ListingImagesUpdate`: `images` (0–10) con `asset_id` e `is_cover` opcional; como máximo una portada (si ninguna, la primera).
- Cada `asset_id` debe ser del autor y estar libre o ya asociado a **este** anuncio → si no, **400**.
- Sustituye el conjunto en una transacción: borra las filas actuales de `listing_image` e inserta las nuevas con `position` = índice. Los `media_asset` que dejan de usarse no se borran (quedan huérfanos, TK-021 §8).
- **200** `Listing`.

### 3.4 Pruebas

- Autor: cambio de cada campo, cambio parcial, precio a `null` (moneda también), moneda sin precio (**422**), título en blanco (**422**, datos intactos), categoría inactiva (**422**).
- Imágenes: reordenar, cambiar la portada, quitar todas, añadir una ajena (**400**), dos portadas (**422**), 11 imágenes (**422**).
- Otros usuarios: miembro no autor (**403**), administrador de la comunidad (**403**), anuncio eliminado (**404**), anuncio `hidden` (**403** para el autor).

## 4. Criterios de aceptación

**AC1 — Edición correcta (HU-08 AC1)**
- **Given** que soy el autor de un anuncio
- **When** cambio su título, precio y tipo con `PATCH`, y reordeno sus imágenes con `PUT …/images`
- **Then** recibo `200` con los datos nuevos y `published_at` sin cambios

**AC2 — Validación (HU-08 AC2)**
- **Given** que soy el autor
- **When** envío `{"title": "  "}` o `{"description": null}`
- **Then** recibo `422` con el campo afectado y el anuncio no cambia

**AC3 — Solo el autor (HU-08 AC3)**
- **Given** un anuncio de otro vecino de mi comunidad
- **When** intento `PATCH` o `PUT …/images`
- **Then** recibo `403` y no se modifica nada

## 5. Plan de tareas

1. Regla común de acceso para edición.
2. `UpdateListing` con coherencia del precio, y pruebas unitarias.
3. `ReplaceListingImages`, y pruebas unitarias.
4. Endpoints y pruebas de integración; verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s -X PATCH http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $AUTOR" \
  -H 'Content-Type: application/json' -d '{"title":"Bicicleta infantil 16\"","price":40}'
curl -s -X PUT http://localhost:8000/v1/listings/<id>/images -H "Authorization: Bearer $AUTOR" \
  -H 'Content-Type: application/json' -d '{"images":[{"asset_id":"<b>","is_cover":true},{"asset_id":"<a>"}]}'
curl -s -o /dev/null -w '%{http_code}\n' -X PATCH http://localhost:8000/v1/listings/<id> \
  -H "Authorization: Bearer $OTRO" -H 'Content-Type: application/json' -d '{"title":"x"}'   # 403
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Editar un anuncio retirado:** se bloquea (asumido); revisar con negocio si el autor debería poder corregirlo y pedir que se restaure.
