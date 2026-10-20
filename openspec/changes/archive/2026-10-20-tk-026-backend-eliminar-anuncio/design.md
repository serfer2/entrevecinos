## Context

TK-022 dejó `ListingRepository` (`get` ya filtra `deleted_at IS NULL`) y TK-021 la regla de lectura de imágenes (también lo filtra).

## Goals / Non-Goals

**Goals:** borrado lógico con los permisos del contrato; ninguna lectura devuelve anuncios eliminados.

**Non-Goals:** retirada por moderación (TK-042); purga de imágenes.

## Decisions

- **Permisos en `DeleteListing`:** el autor siempre (aunque ya no sea miembro); si no, `CommunityAccess.has_role(COMMUNITY_MANAGERS)` (incluye `platform_admin`); si no, `PermissionDenied`.
- **Eliminado = `404`:** `get` no lo encuentra, así que borrar dos veces responde `404`.
- **Filtro centralizado:** las lecturas parten de `listing_with_owner()` + `deleted_at IS NULL`; los listados (TK-028) reutilizarán esa base.

## Risks / Trade-offs

- [Las imágenes del anuncio se conservan en el almacenamiento] → purga posterior tras un periodo de retención.
