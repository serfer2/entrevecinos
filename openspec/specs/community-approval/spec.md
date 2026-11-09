# community-approval Specification

## Purpose
Revisión de las comunidades por un `platform_admin` (`/v1/admin/communities`): listar las pendientes y aprobarlas.
## Requirements
### Requirement: Listar comunidades para su aprobación
`GET /v1/admin/communities` SHALL devolver, solo a un `platform_admin`, las comunidades paginadas de la más antigua a la más reciente, filtradas por `is_active` si se indica.

#### Scenario: Pendientes
- **WHEN** un `platform_admin` llama con `is_active=false`
- **THEN** recibe solo las comunidades pendientes, la más antigua primero

### Requirement: Aprobar una comunidad
`PATCH /v1/admin/communities/{id}` con `{"is_active": true}` SHALL activar la comunidad (sin cambios si ya lo estaba) y responder `200` con `Community`; `is_active: false` u otros campos MUST responder `422` y una comunidad inexistente `404`.

#### Scenario: Aprobación
- **WHEN** un `platform_admin` aprueba una comunidad pendiente
- **THEN** recibe `is_active: true` y la comunidad aparece en `GET /v1/communities`

#### Scenario: Desactivar no disponible
- **WHEN** se envía `{"is_active": false}`
- **THEN** la respuesta es `422`

### Requirement: Rechazar una comunidad pendiente
`DELETE /v1/admin/communities/{community_id}` SHALL permitir solo a un `platform_admin` eliminar una comunidad pendiente de aprobación (`is_active = false`) junto con la membresía de su creador, y responder `204`. Una comunidad activa MUST responder `409 {"detail": "Solo se pueden rechazar comunidades pendientes de aprobación."}` y seguir activa; una inexistente, `404`; un usuario sin rol de plataforma, `403`. Tras el rechazo, la comunidad MUST NOT aparecer en `GET /v1/admin/communities` ni en `GET /v1/users/me/memberships` de su creador, y el creador SHALL poder crear otra comunidad.

#### Scenario: Rechazar
- **WHEN** un `platform_admin` rechaza la comunidad pendiente de un vecino
- **THEN** recibe `204` y la comunidad deja de aparecer en el listado de administración y en las comunidades del creador

#### Scenario: El creador puede crear otra
- **WHEN** el creador de una comunidad rechazada crea otra
- **THEN** la respuesta es `201`

#### Scenario: Comunidad activa
- **WHEN** un `platform_admin` intenta rechazar una comunidad activa
- **THEN** la respuesta es `409` y la comunidad sigue activa

#### Scenario: Sin rol de plataforma
- **WHEN** un vecino o un `community_admin` intenta rechazar una comunidad
- **THEN** la respuesta es `403`

### Requirement: Aviso por correo de una comunidad nueva
Cuando `POST /v1/communities` crea una comunidad pendiente de aprobación, la API SHALL enviar en segundo plano un correo a cada `platform_admin` con la cuenta activa y no borrada, por separado, con el asunto «Nueva comunidad pendiente: {comunidad}», los datos de la comunidad (nombre, descripción, ciudad, código postal y fecha de creación), los del creador (nombre, correo, teléfono y fecha de alta) y el enlace `{WEB_PUBLIC_URL}/admin/comunidades#comunidad-{community_id}`. Una comunidad creada activa por un `platform_admin` MUST NOT generar aviso. Cada aviso SHALL consumir una plaza del cupo; sin cupo, la comunidad MUST crearse igual y no SHALL enviarse el aviso. La respuesta del endpoint no cambia.

#### Scenario: Comunidad de un vecino
- **WHEN** un vecino crea una comunidad y hay dos `platform_admin`
- **THEN** la respuesta es `201` y cada `platform_admin` recibe su propio «Nueva comunidad pendiente: {comunidad}» con los datos del creador y el enlace

#### Scenario: Comunidad de un platform_admin
- **WHEN** un `platform_admin` crea una comunidad
- **THEN** no se envía ningún aviso

#### Scenario: Sin cupo
- **WHEN** un vecino crea una comunidad con el cupo agotado
- **THEN** la respuesta es `201`, la comunidad queda pendiente y no se envía el aviso

### Requirement: Solo administradores de plataforma
Los endpoints de `/v1/admin/communities` MUST responder `403` a cualquier usuario sin rol `platform_admin` y `401` sin autenticación.

#### Scenario: Vecino
- **WHEN** un usuario sin rol `platform_admin` lista o aprueba comunidades
- **THEN** recibe `403`

