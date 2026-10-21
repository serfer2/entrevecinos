## Why

HU-26: registrarse de nuevo con un correo pendiente de validación respondía «El correo ya está en uso.», sin salida para el usuario. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-26-recibir-de-nuevo-el-correo-de-validacion/TK-059-backend-reenvio-del-correo-de-validacion.md`.

## What Changes

- `POST /v1/auth/register`: `409` con `code` (`email_in_use` o `email_pending_verification`), esquema `RegistrationConflict`.
- Nuevo `POST /v1/auth/email-verification/resend` (público): siempre `202`; con una cuenta pendiente crea un enlace nuevo y lo envía, salvo si el último tiene menos de 60 segundos.
- Caso de uso `ResendEmailVerification` y `EmailVerificationRepository.last_created_at`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `user-registration`: correo pendiente al registrarse.
- `email-verification`: reenvío del enlace.

## Impact

- `apps/api` (área `users`), `docs/api` (`auth_register`, `auth_email_verification_resend`, `RegistrationConflict`, `ResendVerificationRequest`).
