## ADDED Requirements

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
`PATCH /v1/communities/{id}/memberships/{user_id}` SHALL permitir a `community_admin` o `platform_admin` pasar una solicitud `pending` a `approved` (fijando `reviewed_by`, `reviewed_at` y `joined_at`) o a `rejected` (fijando `reviewed_by` y `reviewed_at`). Otra transición MUST responder `409 {"detail": "La solicitud ya se ha revisado."}`; una membresía inexistente `404`; `blocked` o `role`, `422`.

#### Scenario: Aprobar
- **WHEN** el administrador envía `{"status": "approved"}` para una solicitud pendiente
- **THEN** recibe `200` con `status: "approved"`, `reviewed_by` = su id y `joined_at` informado

#### Scenario: Revisar dos veces
- **WHEN** se intenta aprobar una solicitud ya rechazada
- **THEN** la respuesta es `409`
