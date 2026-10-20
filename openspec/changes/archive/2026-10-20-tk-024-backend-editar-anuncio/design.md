## Context

TK-022 dejó la publicación (`normalize_price`, validación de categoría e imágenes); TK-036 `ListingVisibility`.

## Goals / Non-Goals

**Goals:** edición atómica; mismas reglas de validación que la publicación; imágenes reutilizables solo dentro del mismo anuncio.

**Non-Goals:** cambios de estado (TK-042, TK-044).

## Decisions

- **`EditableListing`** (regla común): anuncio no eliminado (404), autor (403), membresía aprobada del autor (`require_member`, 403) y no `hidden` → `ListingLocked` (403 `{"detail": "Este anuncio ha sido retirado por la administración de la comunidad."}`).
- **`UNSET` compartido** (`application/unset.py`) entre el perfil y los anuncios para distinguir «no enviado» de `null`.
- **Precio sobre el resultado:** `price: null` borra también la moneda; un precio sin moneda conserva la actual o usa `EUR`; una moneda sin precio resultante → 422 en `currency`.
- **`published_at` no cambia** al editar.
- **Imágenes:** `MediaRepository.owned_available(ids, user, listing_id)` acepta las del autor libres o ya en este anuncio; el repositorio borra e inserta el conjunto en la misma transacción (`position` = índice; portada la marcada o la primera).

## Risks / Trade-offs

- [Editar un anuncio retirado está bloqueado] → decisión revisable con negocio.
- [Las imágenes que dejan de usarse quedan huérfanas] → limpieza posterior (TK-021 §8).
