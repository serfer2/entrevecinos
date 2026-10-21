## MODIFIED Requirements

### Requirement: Registro de cuenta
`POST /v1/auth/register` SHALL crear una cuenta inactiva (`is_active = false`, `email_verified_at` nulo) con rol `user` a partir de `email`, `password`, `full_name` y `phone` opcional, enviar el correo de validación tras responder y responder `201` con `RegistrationResponse` (`email`, `verification_expires_at`). La respuesta MUST NOT incluir un token de acceso.

#### Scenario: Registro correcto
- **WHEN** se envía un correo no registrado, una contraseña de 12 a 128 caracteres y un nombre
- **THEN** la respuesta es `201` sin `access_token`, la cuenta queda inactiva, la contraseña se guarda como hash Argon2id y se envía un correo con el enlace `{WEB_PUBLIC_URL}/verificar-correo?token=…`

#### Scenario: Fallo del SMTP
- **WHEN** el servidor de correo no responde durante el registro
- **THEN** la respuesta sigue siendo `201`, la cuenta existe y el error queda en el log
