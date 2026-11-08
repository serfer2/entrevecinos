## ADDED Requirements

### Requirement: Sesiones anteriores al cambio de contraseña
La API MUST rechazar con `401` un JWT cuyo `iat` sea anterior a `users.password_changed_at`, truncada al segundo. Un JWT emitido después del cambio SHALL seguir valiendo. Reescribir el hash al iniciar sesión (parámetros de Argon2 antiguos) MUST NOT cambiar `password_changed_at`.

#### Scenario: Sesión anterior al cambio
- **WHEN** se usa en `GET /v1/users/me` un JWT emitido antes de restablecer la contraseña
- **THEN** la respuesta es `401`

#### Scenario: Sesión nueva
- **WHEN** se inicia sesión con la contraseña nueva y se usa ese JWT
- **THEN** la respuesta es `200`
