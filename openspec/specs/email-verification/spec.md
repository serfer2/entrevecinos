# email-verification Specification

## Purpose
Enlace de validación del correo y su validación (`POST /v1/auth/email-verification`).
## Requirements
### Requirement: Enlace de validación
Cada enlace de validación SHALL llevar un token aleatorio (`secrets.token_urlsafe(32)`) del que solo se guarda el SHA-256, caducar a las `EMAIL_VERIFICATION_TTL_HOURS` (24 por defecto) y sustituir a los enlaces anteriores del mismo usuario. El correo, en español con texto y HTML, SHALL saludar con el nombre, incluir el enlace y avisar de la caducidad.

#### Scenario: Enlace sustituido
- **WHEN** se emite un enlace nuevo para un usuario que ya tenía otro
- **THEN** el anterior deja de ser válido

### Requirement: Validar el correo
`POST /v1/auth/email-verification` (público, cuerpo `{"token": "..."}` sin campos adicionales) SHALL, con un token vigente, activar la cuenta (`is_active = true`, `email_verified_at = now`), borrar sus tokens y responder `200` con `AuthResponse`. Con un token caducado MUST responder `410` con `code: "verification_expired"` y el `email` de la cuenta, sin activarla; con un token desconocido, ya usado o sustituido, `400` con `code: "verification_invalid"`.

#### Scenario: Token vigente
- **WHEN** se valida un token emitido hace menos de 24 horas
- **THEN** la respuesta es `200` con un JWT y la cuenta queda activa y validada

#### Scenario: Token caducado
- **WHEN** se valida un token emitido hace más de 24 horas
- **THEN** la respuesta es `410` con `code: "verification_expired"` y el correo, y la cuenta sigue inactiva

#### Scenario: Token ya usado
- **WHEN** se valida dos veces el mismo token
- **THEN** la segunda respuesta es `400` con `code: "verification_invalid"`
