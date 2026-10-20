## Context

TK-015 dejó las solicitudes de acceso y `MembershipRepository`. Contrato: `communities_community_id_memberships.yaml` (`get`), `communities_community_id_memberships_user_id.yaml` (`patch`), `MembershipUpdate`.

## Goals / Non-Goals

**Goals:** un único punto de decisión de permisos por comunidad; revisión de solicitudes con transiciones explícitas; documentar la extensión `status` del error.

**Non-Goals:** bloqueo, expulsión y roles (TK-040).

## Decisions

- **`CommunityAccess` en `application/authorization/`**, sin framework: comprueba primero que la comunidad existe (404), después la membresía. `platform_admin` pasa siempre.
- **`MembershipNotApproved` hereda de `PermissionDenied`:** ambos son 403; el manejador más específico añade `status` (pendiente, rechazada o bloqueada) para que el frontend muestre el aviso adecuado.
- **`require_role` sin membresía aprobada → `PermissionDenied`** (sin `status`): la gestión no necesita distinguir el estado.
- **Transiciones:** solo `pending → approved | rejected`; cualquier otra → `MembershipAlreadyReviewed` (409). Al aprobar se fijan `reviewed_by`, `reviewed_at` y `joined_at` con `statement_timestamp()`.
- **Petición `MembershipUpdate` restringida** a `status` `approved`/`rejected`; `blocked` y `role` → 422 hasta TK-040.
- **Contrato:** `MembershipForbidden` (`oneOf` `Error`/`MembershipError`) en las operaciones que exigen membresía aprobada; `MembershipConflict` en `requestMembership`.

## Risks / Trade-offs

- [Un rechazo es irreversible en el MVP] → documentado (TK-015 §8).
