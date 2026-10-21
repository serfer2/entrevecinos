## MODIFIED Requirements

### Requirement: Crear una comunidad
`POST /v1/communities` SHALL crear la comunidad del usuario autenticado y registrarlo como `community_admin` con membresía `approved` y `joined_at`, respondiendo `201` con el esquema `Community`. La comunidad SHALL crearse con `is_active: false` (pendiente de aprobación), salvo si el creador es `platform_admin`, en cuyo caso SHALL crearse con `is_active: true`. Mientras está pendiente, la comunidad MUST NOT aparecer en `GET /v1/communities` y su detalle, sus solicitudes y sus anuncios SHALL responder `404`.

#### Scenario: Creación correcta
- **WHEN** un usuario autenticado envía `{"name": "Urbanización Los Olivos", "city": "Majadahonda", "postal_code": "28220"}`
- **THEN** recibe `201` con `created_by` igual a su id e `is_active: false`, y existe su membresía `community_admin`/`approved`

#### Scenario: Comunidad pendiente oculta
- **WHEN** otro usuario busca comunidades o solicita el acceso a una comunidad pendiente
- **THEN** no la encuentra y la solicitud responde `404`

#### Scenario: Creada por un administrador de plataforma
- **WHEN** un `platform_admin` crea una comunidad
- **THEN** recibe `201` con `is_active: true` y la comunidad aparece en `GET /v1/communities`
