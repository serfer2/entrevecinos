## Why

HU-44 (Épica 8): el vecino no sabe cuándo se aprueba su solicitud de acceso y tiene que volver a entrar para comprobarlo. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-44-recibir-un-aviso-por-correo-cuando-me-aceptan-en-una-comunidad/TK-108-backend-aviso-por-correo-al-aprobar-una-solicitud.md`.

## What Changes

- **Aviso «Ya eres miembro de {comunidad}»** al solicitante cuando su membresía pasa de `pending` a `approved` con `PATCH /v1/communities/{community_id}/memberships/{user_id}`, la apruebe un `community_admin` o un `platform_admin`; enlace a `/comunidades/{community_id}`.
- **Sin aviso** al rechazar, bloquear o desbloquear, ni si la cuenta del solicitante está inactiva o borrada.
- **Cupo:** una plaza por aviso; sin cupo, la aprobación se hace igual y no se avisa.
- **Envío en segundo plano**; la respuesta no cambia.
- **Contrato:** descripción de `updateMembership`; tabla de cambios de `docs/api/README.md`. **Guía:** el cupo cuenta estos avisos.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `community-access-requests`: aviso por correo al solicitante al aprobar su solicitud.

## Impact

- API: `ChangeMembershipStatus` devuelve también el estado anterior; `MembershipNotices.request_approved`; endpoint `update_membership`; pruebas.
- Contrato y `infra/aws/README.md`, `apps/api/README.md`.
