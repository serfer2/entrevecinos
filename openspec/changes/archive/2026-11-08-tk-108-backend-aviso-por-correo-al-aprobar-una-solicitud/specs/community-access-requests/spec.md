## ADDED Requirements

### Requirement: Aviso por correo al aprobar una solicitud
Cuando `PATCH /v1/communities/{community_id}/memberships/{user_id}` cambia una membresía de `pending` a `approved`, la API SHALL enviar en segundo plano un correo al solicitante, si su cuenta está activa y no borrada, con el asunto «Ya eres miembro de {comunidad}» y el enlace `{WEB_PUBLIC_URL}/comunidades/{community_id}`. Rechazar una solicitud, bloquear o desbloquear a un miembro MUST NOT enviar ningún correo. El aviso SHALL consumir una plaza del cupo; sin cupo, la aprobación MUST hacerse igual y no SHALL enviarse el aviso. La respuesta del endpoint no cambia.

#### Scenario: Solicitud aprobada
- **WHEN** un `community_admin` o un `platform_admin` aprueba una solicitud pendiente
- **THEN** la respuesta es `200` y el solicitante recibe «Ya eres miembro de {comunidad}»

#### Scenario: Rechazo o desbloqueo
- **WHEN** se rechaza una solicitud o se desbloquea a un miembro
- **THEN** no se envía ningún correo

#### Scenario: Sin cupo
- **WHEN** se aprueba una solicitud con el cupo agotado
- **THEN** la respuesta es `200`, el vecino es miembro aprobado y no se envía el aviso
