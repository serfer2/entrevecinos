## Why

HU-47 (Épica 8): una comunidad pendiente que no procede no se puede rechazar; se queda pendiente para siempre y su creador no puede crear otra (HU-23). Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-47-rechazar-una-comunidad-pendiente/TK-112-backend-rechazar-una-comunidad-pendiente.md`.

## What Changes

- Nueva operación `DELETE /v1/admin/communities/{community_id}` (`adminRejectCommunity`, `x-mvp: true`): solo `platform_admin`; elimina una comunidad pendiente y, en cascada, la membresía de su creador (`204`).
- Comunidad activa → `409` «Solo se pueden rechazar comunidades pendientes de aprobación.»; inexistente → `404`; sin rol de plataforma → `403`.
- Tras el rechazo, el creador puede crear otra comunidad.
- **Contrato:** nueva operación, «Cambios» y resumen de `docs/api/README.md`. **Documentación:** `readme.md` (§1.2, MVP y §3.2) y `apps/api/README.md`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `community-approval`: nuevo requisito «Rechazar una comunidad pendiente».

## Impact

- API: `CommunityNotPending` y su manejador, `CommunityRepository.delete_pending` (puerto, SQLAlchemy y *fake*), `RejectCommunity` en `approve_communities.py`, endpoint en `presentation/v1/admin.py`; pruebas.
- Contrato: `docs/api/paths/admin_communities_community_id.yaml`, `docs/api/README.md`.
- Sin migraciones (`community_membership.community_id` ya es `ON DELETE CASCADE`). Sin cambios de infraestructura.
