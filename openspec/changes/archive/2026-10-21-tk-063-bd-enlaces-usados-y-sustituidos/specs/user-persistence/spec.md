## MODIFIED Requirements

### Requirement: Tokens de validación
La tabla `email_verification` SHALL guardar `token_hash` (`CHAR(64)`, PK, SHA-256 del token), `user_id` (FK a `users` con `ON DELETE CASCADE`, indexada), `expires_at`, `created_at`, `used_at` y `superseded_at` (ambas `TIMESTAMPTZ NULL`). El token en claro MUST NOT guardarse. La restricción `ck_email_verification_used_or_superseded` MUST rechazar un enlace usado y sustituido a la vez, y el índice único parcial `uq_email_verification_one_active_per_user` (`WHERE used_at IS NULL AND superseded_at IS NULL`) MUST impedir dos enlaces vigentes del mismo usuario. Emitir un enlace SHALL marcar los vigentes del usuario como sustituidos y borrar los suyos caducados hace más de 30 días; validar el correo SHALL marcar el enlace como usado y sustituir el resto.

#### Scenario: Borrado del usuario
- **WHEN** se borra un usuario con tokens de validación
- **THEN** sus tokens desaparecen

#### Scenario: Enlace sustituido
- **WHEN** se emite un enlace nuevo para un usuario con otro vigente
- **THEN** el anterior se conserva con `superseded_at` y solo el nuevo está vigente

#### Scenario: Dos enlaces vigentes
- **WHEN** se inserta un segundo enlace vigente para el mismo usuario
- **THEN** la base de datos lo rechaza por `uq_email_verification_one_active_per_user`
