## MODIFIED Requirements

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

## ADDED Requirements

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
