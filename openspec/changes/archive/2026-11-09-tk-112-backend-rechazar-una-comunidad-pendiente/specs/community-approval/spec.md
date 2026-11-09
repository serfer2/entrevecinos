## ADDED Requirements

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
