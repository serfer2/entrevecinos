## MODIFIED Requirements

### Requirement: Enlace de validación
Cada enlace de validación SHALL llevar un token aleatorio (`secrets.token_urlsafe(32)`) del que solo se guarda el SHA-256, caducar a las `EMAIL_VERIFICATION_TTL_HOURS` (24 por defecto) y sustituir a los enlaces anteriores del mismo usuario, que se conservan marcados como sustituidos. El correo, en español con texto y HTML, SHALL saludar con el nombre, incluir el enlace y avisar de la caducidad.

#### Scenario: Enlace sustituido
- **WHEN** se emite un enlace nuevo para un usuario que ya tenía otro
- **THEN** el anterior deja de ser válido

### Requirement: Validar el correo
`POST /v1/auth/email-verification` (público, cuerpo `{"token": "..."}` sin campos adicionales) SHALL, con un token vigente, activar la cuenta (`is_active = true`, `email_verified_at = now`), marcar el enlace como usado y responder `200` con `AuthResponse`. Si el token no vale, MUST responder, en este orden: `400` `verification_invalid` si no existe o su usuario no existe o está eliminado; `400` `email_already_verified` («Tu correo ya está validado.») si la cuenta ya tiene el correo validado; `400` `verification_superseded` («Este enlace ya no es válido porque te hemos enviado uno más reciente.») con el `email` si otro enlace lo sustituyó; y `410` `verification_expired` con el `email` si ha caducado. En ningún caso se activa la cuenta.

#### Scenario: Token vigente
- **WHEN** se valida un token emitido hace menos de 24 horas
- **THEN** la respuesta es `200` con un JWT y la cuenta queda activa y validada

#### Scenario: Token caducado
- **WHEN** se valida un token emitido hace más de 24 horas
- **THEN** la respuesta es `410` con `code: "verification_expired"` y el correo, y la cuenta sigue inactiva

#### Scenario: Token ya usado
- **WHEN** se valida dos veces el mismo token
- **THEN** la segunda respuesta es `400` con `code: "email_already_verified"`

#### Scenario: Token sustituido con la cuenta pendiente
- **WHEN** se valida el token de un correo anterior a un reenvío y la cuenta sigue pendiente
- **THEN** la respuesta es `400` con `code: "verification_superseded"` y el correo, y la cuenta sigue inactiva

#### Scenario: Token sustituido con la cuenta validada
- **WHEN** se valida el token de un correo anterior después de validar la cuenta con el último
- **THEN** la respuesta es `400` con `code: "email_already_verified"`

#### Scenario: Token desconocido
- **WHEN** se valida un token que nunca se ha emitido
- **THEN** la respuesta es `400` con `code: "verification_invalid"` y sin correo
