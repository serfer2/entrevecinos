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

### Requirement: Solo administradores de plataforma
Los endpoints de `/v1/admin/communities` MUST responder `403` a cualquier usuario sin rol `platform_admin` y `401` sin autenticación.

#### Scenario: Vecino
- **WHEN** un usuario sin rol `platform_admin` lista o aprueba comunidades
- **THEN** recibe `403`

