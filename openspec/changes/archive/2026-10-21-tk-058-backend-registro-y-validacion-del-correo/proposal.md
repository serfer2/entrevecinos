## Why

HU-25: la cuenta debe quedar inactiva hasta que el usuario abra el enlace que recibe por correo, válido 24 horas. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-25-validar-mi-correo-electronico-al-registrarme/TK-058-backend-registro-y-validacion-del-correo.md`.

## What Changes

- **BREAKING** `POST /v1/auth/register` crea la cuenta inactiva, envía el correo de validación y responde `201` con `RegistrationResponse` (`email`, `verification_expires_at`), sin JWT.
- Nuevo `POST /v1/auth/email-verification` (público): activa la cuenta y devuelve `AuthResponse`; `410` si el token caducó (con el correo) y `400` si no es válido.
- `POST /v1/auth/token`: `403` `email_not_verified` para cuentas sin validar que no son `platform_admin`.
- Puertos `EmailSender` (adaptador `SmtpEmailSender`) y `EmailVerificationRepository`; casos de uso `VerifyEmail` y `EmailVerificationIssuer`.

## Capabilities

### New Capabilities
- `email-verification`: emisión y validación del enlace de validación del correo.

### Modified Capabilities
- `user-registration`: registro sin sesión y con correo de validación.
- `user-authentication`: inicio de sesión bloqueado sin validar el correo.

## Impact

- `apps/api` (área `users`, `infrastructure/mail`), `docs/api` (`auth_register`, `auth_token`, `auth_email_verification`, esquemas nuevos). La web se adapta en TK-060.
