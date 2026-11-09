## Context

`ApproveCommunity` activa una comunidad con `CommunityRepository.activate`. `CommunityRepository.get` oculta las inactivas, así que una pendiente no admite membresías nuevas ni anuncios: solo tiene la membresía de su creador, que se borra en cascada.

## Goals / Non-Goals

**Goals:** rechazar (eliminar) comunidades pendientes, solo `platform_admin`.

**Non-Goals:** desactivar o borrar comunidades activas; avisar al creador; la web (TK-113).

## Decisions

- **Rechazar = eliminar** la fila de `community`: sin migración ni estado nuevo, y libera la regla de una pendiente por usuario (TK-053). La pérdida del historial se acepta (ticket §8).
- **`delete_pending(community_id) -> Community | None`**: lee con `FOR UPDATE`, borra solo si está inactiva y devuelve la comunidad borrada; `None` si no existe; si está activa lanza `CommunityNotPending`. El bloqueo serializa un rechazo y una aprobación simultáneos. El ticket proponía devolver un resultado enumerado; lanzar el error de dominio desde el repositorio sigue el precedente de `add` (`PendingCommunityExists`) y simplifica el caso de uso.
- **`RejectCommunity`** junto a `ApproveCommunity`, con el mismo `_require_platform_admin`.

## Risks / Trade-offs

- [Anuncios en una pendiente] → imposibles con las reglas actuales; si existieran, `listing.community_id ON DELETE RESTRICT` haría fallar el borrado en vez de perder datos.
