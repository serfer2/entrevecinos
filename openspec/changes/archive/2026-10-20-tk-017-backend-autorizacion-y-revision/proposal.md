## Why

HU-06: el administrador revisa las solicitudes de acceso, y solo él puede hacerlo. Además, anuncios y administración necesitan una única política de permisos por comunidad. Ticket: `docs/product/tickets/EP-02-comunidades/HU-06-aprobar-o-rechazar-solicitudes-de-acceso/TK-017-backend-autorizacion-y-revision-de-solicitudes.md`.

## What Changes

- Política `CommunityAccess` (`require_member`, `require_role`) y errores `PermissionDenied` y `MembershipNotApproved` → `403` (este último con `status`).
- `GET /v1/communities/{id}/memberships` y `PATCH /v1/communities/{id}/memberships/{user_id}` (`approved` / `rejected`).
- Contrato: `MembershipError`, `MembershipForbidden` (403) y `MembershipConflict` (409) en `docs/api`.

## Capabilities

### New Capabilities
- `community-authorization`: política de permisos por comunidad y revisión de solicitudes.

### Modified Capabilities
- `community-access-requests`: el `409` de solicitud duplicada queda documentado como `MembershipConflict`.

## Impact

- `apps/api` y `docs/api`.
