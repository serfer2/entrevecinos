## ADDED Requirements

### Requirement: Correo validado
La tabla `users` SHALL tener `email_verified_at TIMESTAMPTZ NULL` y la restricción `ck_users_active_requires_verified_email`, que MUST rechazar una cuenta activa sin correo validado salvo con rol `platform_admin`. La migración `0008` SHALL dar por validadas las cuentas existentes (`email_verified_at = created_at`).

#### Scenario: Cuenta activa sin validar
- **WHEN** se guarda una cuenta `user` con `is_active = true` y `email_verified_at` nulo
- **THEN** la base de datos la rechaza por `ck_users_active_requires_verified_email`

#### Scenario: Administrador de plataforma sin validar
- **WHEN** se guarda una cuenta `platform_admin` activa con `email_verified_at` nulo
- **THEN** se acepta

### Requirement: Tokens de validación
La tabla `email_verification` SHALL guardar `token_hash` (`CHAR(64)`, PK, SHA-256 del token), `user_id` (FK a `users` con `ON DELETE CASCADE`, indexada), `expires_at` y `created_at`. El token en claro MUST NOT guardarse.

#### Scenario: Borrado del usuario
- **WHEN** se borra un usuario con tokens de validación
- **THEN** sus tokens desaparecen
