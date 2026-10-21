## ADDED Requirements

### Requirement: Una comunidad pendiente por usuario
`POST /v1/communities` MUST responder `409` con «Ya tienes una comunidad pendiente de aprobación.» y no crear nada cuando el usuario ya creó una comunidad que sigue pendiente; tras su aprobación SHALL poder crear otra. El límite no se aplica a un `platform_admin`, cuyas comunidades nacen activas.

#### Scenario: Segunda comunidad pendiente
- **WHEN** un usuario con una comunidad pendiente crea otra
- **THEN** recibe `409` y no se crea la comunidad

#### Scenario: Tras la aprobación
- **WHEN** su comunidad pendiente se aprueba y crea otra
- **THEN** recibe `201` con `is_active: false`
