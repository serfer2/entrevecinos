## Context

`update_membership` solo admite `status` y lo resuelve `ChangeMembershipStatus` (revisión, bloqueo y desbloqueo, con el aviso de TK-108). El rol de una membresía solo se fija al crear la comunidad (`CreateCommunity`, el creador queda `community_admin`). `RemoveMembership` ya protege al último administrador con `count_admins`.

## Goals / Non-Goals

**Goals:** que un `platform_admin` nombre o quite administradores de una comunidad sin dejarla nunca sin administrador.

**Non-Goals:** rol `moderator`; que un `community_admin` nombre a otros; avisos por correo; la web (TK-110).

## Decisions

- **Caso de uso aparte, `ChangeMembershipRole`**, en `review_membership.py` junto a `ChangeMembershipStatus`: las reglas (quién, qué estado, último administrador) no se parecen a las transiciones de estado, y así el aviso de TK-108 sigue ligado solo a `status`.
- **Permiso:** el caso de uso llama a `CommunityAccess.require_role(actor, community_id, COMMUNITY_ADMINS)` (que da el `404` de comunidad inexistente y deja pasar al `platform_admin`) y después exige `platform_role is PLATFORM_ADMIN`; si no, `PermissionDenied`. La política sigue en `CommunityAccess` y el caso de uso solo la estrecha.
- **Exactamente uno de `status` o `role`** con un `model_validator` de Pydantic: un único cambio por petición simplifica errores y el despacho del endpoint. Los campos pasan a opcionales y conservan sus `Literal`.
- **Último administrador sin carreras:** `count_admins(community_id, lock=True)` selecciona las filas de administradores aprobados con `FOR UPDATE` y las cuenta; dos degradaciones simultáneas se serializan y la segunda ve un solo administrador. Sin `lock`, el comportamiento actual no cambia.
- **`set_role` no toca `reviewed_by`/`reviewed_at`**: describen la revisión de la solicitud, no el nombramiento.
- **Mismo rol → `200` sin escribir**: la operación es idempotente y no exige comprobar el último administrador.

## Risks / Trade-offs

- [El contrato decía que un `community_admin` asigna el rol] → se reescribe la descripción: HU-45 lo reserva a la plataforma. Delegarlo después solo cambiaría la comprobación de permiso.
- [Un `platform_admin` sin membresía no puede nombrarse a sí mismo] → no lo necesita: ya gestiona cualquier comunidad (HU-31); `set_role` sobre una membresía inexistente responde `404`.
