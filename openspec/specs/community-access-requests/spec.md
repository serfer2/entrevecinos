# community-access-requests Specification

## Purpose
Búsqueda de comunidades, solicitudes de acceso y listado de las membresías propias.
## Requirements
### Requirement: Buscar comunidades
`GET /v1/communities` SHALL devolver las comunidades activas que coinciden con `q` (nombre o descripción), `city` y `postal_code` (por prefijo), combinados con `AND`, sin distinguir mayúsculas ni tildes, ordenadas por nombre.

#### Scenario: Coincidencia sin tildes
- **WHEN** existen «Urbanización Los Olivos» (Majadahonda, 28220) y «Barrio del Pilar» (Madrid, 28029) y se busca `q=Olívos`, `city=majadahonda` o `postal_code=282`
- **THEN** se obtiene solo la primera (con `postal_code=282` también «Barrio del Pilar»)

### Requirement: Solicitar el acceso
`POST /v1/communities/{community_id}/memberships` SHALL crear una membresía `pending` con rol `member` para el usuario autenticado y responder `201` con el esquema `Membership`; comunidad inexistente o desactivada → `404`.

#### Scenario: Solicitud
- **WHEN** un usuario sin membresía solicita el acceso
- **THEN** recibe `201` con `status: "pending"` y la solicitud aparece en `GET /v1/users/me/memberships`

### Requirement: Sin solicitudes duplicadas
Si el usuario ya tiene una membresía en la comunidad, en cualquier estado, la solicitud MUST responder `409 {"detail": "Ya tienes una membresía en esta comunidad.", "status": "<estado>"}` sin crear otra. El contrato documenta este cuerpo como `MembershipConflict` (`MembershipError`).

#### Scenario: Ya pendiente
- **WHEN** el usuario vuelve a solicitar el acceso
- **THEN** recibe `409` con `status: "pending"`

### Requirement: Mis membresías
`GET /v1/users/me/memberships` SHALL devolver `{items: MyMembership[]}` del usuario autenticado, filtrable por `status`, ordenado por `requested_at` descendente; las comunidades desactivadas solo aparecen si la membresía está aprobada.

#### Scenario: Filtro por estado
- **WHEN** se pide `status=approved`
- **THEN** solo aparecen las membresías aprobadas

### Requirement: Aviso por correo a la administración
Al crear una solicitud con `POST /v1/communities/{community_id}/memberships`, la API SHALL enviar en segundo plano un correo a cada miembro `approved` con rol `community_admin` de la comunidad cuya cuenta esté activa y no borrada, uno por destinatario. El correo SHALL tener el asunto «Nueva solicitud para unirse a {comunidad}», el nombre del solicitante y el enlace `{WEB_PUBLIC_URL}/comunidades/{community_id}/gestion/solicitudes`, y MUST NOT incluir el correo ni el teléfono del solicitante. Los miembros, moderadores y administradores no aprobados MUST NOT recibirlo. La respuesta del endpoint no cambia.

#### Scenario: Comunidad con dos administradores y un moderador
- **WHEN** un vecino solicita unirse
- **THEN** la respuesta es `201` y se envían dos correos, uno a cada administrador

#### Scenario: Solicitud repetida
- **WHEN** un vecino con una membresía en la comunidad vuelve a solicitarla
- **THEN** la respuesta es `409` y no se envía ningún correo

### Requirement: Cupo de los avisos de solicitud
Cada aviso SHALL consumir una plaza del cupo de correos del periodo. Sin cupo, la solicitud MUST crearse igual y no SHALL enviarse ningún aviso más.

#### Scenario: Sin cupo
- **WHEN** un vecino solicita unirse con el cupo agotado
- **THEN** la respuesta es `201`, la solicitud queda `pending` y no se envía ningún aviso

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

