## Why

HU-45 (Épica 8): solo es administrador de una comunidad quien la crea, y no hay forma de nombrar a otro; la API rechaza `role` con `422`. El administrador de plataforma debe poder decidir quién administra cada comunidad. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-45-nombrar-a-los-administradores-de-una-comunidad/TK-109-backend-cambiar-el-rol-de-un-miembro.md`.

## What Changes

- `PATCH /v1/communities/{community_id}/memberships/{user_id}` admite `{"role": "member" | "community_admin"}`, solo para `platform_admin` (`403` para el resto).
- Cada petición lleva exactamente uno de `status` o `role` (`422` si van los dos o ninguno); `moderator` → `422`.
- Solo membresías `approved` (`409` «Solo se puede cambiar el rol de un miembro aprobado.»); quitar el rol al último administrador → `409` «La comunidad debe tener al menos un administrador.». Mismo rol → `200` sin cambios.
- Sin correo al cambiar el rol.
- **Contrato:** descripción del `PATCH`, `MembershipUpdate`, ejemplo y `409`; tabla de cambios de `docs/api/README.md`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `community-authorization`: «Revisar una solicitud» deja de rechazar `role` con `422`; nuevo requisito «Cambiar el rol de un miembro».

## Impact

- API: `MembershipUpdateRequest`, nuevo caso de uso `ChangeMembershipRole`, `MembershipRepository.set_role` (puerto y SQLAlchemy, con bloqueo de las filas de administradores), errores de `MembershipChangeRejected`, endpoint `update_membership`; pruebas.
- Contrato: `docs/api/paths/communities_community_id_memberships_user_id.yaml`, `docs/api/components/schemas/MembershipUpdate.yaml`, `docs/api/README.md`.
- Sin migraciones: `community_memberships.role` ya existe. Sin cambios de infraestructura.
