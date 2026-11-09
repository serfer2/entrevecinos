# community-authorization Specification

## Purpose
Política de permisos por comunidad (`CommunityAccess`) y revisión de solicitudes de acceso.
## Requirements
### Requirement: Política de acceso por comunidad
`CommunityAccess.require_member` SHALL exigir una membresía `approved` en la comunidad (o `platform_admin`); sin membresía MUST lanzar `PermissionDenied` y con una membresía no aprobada `MembershipNotApproved(status)`. `require_role` SHALL exigir además uno de los roles indicados. Una comunidad inexistente MUST responder `404` antes de comprobar permisos.

#### Scenario: Membresía pendiente
- **WHEN** un usuario con membresía `pending` accede a una operación que exige membresía
- **THEN** la API responde `403 {"detail": "Tu membresía en esta comunidad no está aprobada.", "status": "pending"}`

#### Scenario: Sin permisos
- **WHEN** un miembro aprobado sin rol de administrador llama a la gestión de membresías
- **THEN** la API responde `403 {"detail": "No tienes permisos para realizar esta acción."}`

### Requirement: Ver las solicitudes
`GET /v1/communities/{id}/memberships` SHALL devolver, a `community_admin`, `moderator` o `platform_admin`, las membresías paginadas (filtro `status`), de la más antigua a la más reciente, con `user` como `UserSummary` y sin correo ni teléfono.

#### Scenario: Pendientes
- **WHEN** el administrador pide `status=pending`
- **THEN** recibe las solicitudes pendientes con el nombre de cada solicitante

### Requirement: Revisar una solicitud
`PATCH /v1/communities/{id}/memberships/{user_id}` SHALL permitir a `community_admin` o `platform_admin` pasar una solicitud `pending` a `approved` (fijando `reviewed_by`, `reviewed_at` y `joined_at`) o a `rejected` (fijando `reviewed_by` y `reviewed_at`). Otra transición MUST responder `409 {"detail": "La solicitud ya se ha revisado."}`; una membresía inexistente `404`; `status: blocked` sobre una solicitud pendiente, `409`. El cuerpo MUST llevar exactamente uno de `status` o `role`; ambos o ninguno responden `422`.

#### Scenario: Aprobar
- **WHEN** el administrador envía `{"status": "approved"}` para una solicitud pendiente
- **THEN** recibe `200` con `status: "approved"`, `reviewed_by` = su id y `joined_at` informado

#### Scenario: Revisar dos veces
- **WHEN** se intenta aprobar una solicitud ya rechazada
- **THEN** la respuesta es `409`

#### Scenario: Estado y rol a la vez
- **WHEN** se envía `{"status": "approved", "role": "community_admin"}`
- **THEN** la respuesta es `422`

### Requirement: Bloquear y desbloquear miembros
`PATCH /v1/communities/{id}/memberships/{user_id}` SHALL permitir a `community_admin` o `platform_admin` bloquear a un miembro aprobado (`blocked`) y desbloquearlo (`approved`, conservando `joined_at`). Bloquear a un administrador o a uno mismo, o cualquier otra transición, MUST responder `409`. Un bloqueado pierde el acceso (403 con `status: blocked`) y no puede volver a solicitarlo.

#### Scenario: Bloquear
- **WHEN** el administrador bloquea a un miembro
- **THEN** el miembro recibe `403` al ver el listado y `409` al volver a solicitar el acceso

#### Scenario: Administrador
- **WHEN** se intenta bloquear a otro administrador
- **THEN** la respuesta es `409 {"detail": "No se puede bloquear a un administrador de la comunidad."}`

### Requirement: Cambiar el rol de un miembro
`PATCH /v1/communities/{id}/memberships/{user_id}` con `{"role": …}` SHALL permitir solo a un `platform_admin` cambiar el rol de una membresía `approved` entre `member` y `community_admin`; cualquier otro usuario, incluido un `community_admin` de la comunidad, MUST recibir `403`. `moderator` MUST responder `422`. Una membresía no aprobada MUST responder `409 {"detail": "Solo se puede cambiar el rol de un miembro aprobado."}`, y quitar el rol al último administrador aprobado `409 {"detail": "La comunidad debe tener al menos un administrador."}`. Enviar el rol actual SHALL responder `200` sin cambios. El cambio de rol MUST NOT modificar `status`, `reviewed_by`, `reviewed_at` ni `joined_at` y no SHALL enviar ningún correo. Un `community_admin` nombrado así SHALL tener los mismos permisos y avisos (TK-106) que quien creó la comunidad.

#### Scenario: Nombrar administrador
- **WHEN** un `platform_admin` envía `{"role": "community_admin"}` para un miembro aprobado
- **THEN** recibe `200` con `role: "community_admin"` y ese usuario puede listar las membresías de la comunidad

#### Scenario: Quitar el rol
- **WHEN** un `platform_admin` envía `{"role": "member"}` para uno de dos administradores
- **THEN** recibe `200`, el usuario sigue `approved` y recibe `403` al listar las membresías

#### Scenario: Último administrador
- **WHEN** un `platform_admin` quita el rol al único administrador
- **THEN** la respuesta es `409 {"detail": "La comunidad debe tener al menos un administrador."}`

#### Scenario: Miembro no aprobado
- **WHEN** se envía `role` para una membresía `pending`, `rejected` o `blocked`
- **THEN** la respuesta es `409` y el rol no cambia

#### Scenario: Administrador de comunidad
- **WHEN** un `community_admin` envía `{"role": "community_admin"}` para un miembro de su comunidad
- **THEN** la respuesta es `403`

### Requirement: Expulsar o salir
`DELETE /v1/communities/{id}/memberships/{user_id}` SHALL eliminar la membresía propia o, para un `community_admin`/`platform_admin`, la de otro (`204`); un administrador MUST NOT expulsar a otro administrador (403) y nunca se elimina al último administrador aprobado (409). Tras la expulsión, el vecino puede volver a solicitar el acceso.

#### Scenario: Último administrador
- **WHEN** el único administrador intenta salir
- **THEN** la respuesta es `409 {"detail": "La comunidad debe tener al menos un administrador."}`

### Requirement: Anuncios de miembros bloqueados o expulsados
Los anuncios de un autor sin membresía aprobada MUST dejar de aparecer en el listado, la búsqueda y su `total`, y su detalle SHALL responder `404` a los miembros (lo ven el autor y los gestores); al desbloquearlo vuelven a mostrarse con su estado original. Un autor `platform_admin` SHALL contar como miembro aprobado de cualquier comunidad (como en `require_member`): sus anuncios se muestran aunque no tenga membresía o la suya no esté aprobada.

#### Scenario: Bloqueo
- **WHEN** se bloquea a un miembro con anuncios
- **THEN** los demás miembros dejan de verlos y vuelven a verlos al desbloquearlo

#### Scenario: Anuncios de un platform_admin
- **WHEN** un `platform_admin` con la solicitud pendiente publica un anuncio en una comunidad
- **THEN** los miembros lo ven en el listado y en su detalle

### Requirement: Listado de miembros
Sin filtro de estado, `GET /v1/communities/{id}/memberships` SHALL ordenar por estado (pendientes, miembros, bloqueados, rechazados) y nombre, con el rol de cada uno.

#### Scenario: Todos los estados
- **WHEN** el administrador pide el listado sin filtro
- **THEN** aparecen primero las solicitudes pendientes

