## Why

HU-25: hay que saber si el correo de cada cuenta está validado y guardar los enlaces de validación con su caducidad, sin que una copia de la base de datos permita usarlos. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-25-validar-mi-correo-electronico-al-registrarme/TK-057-bd-validacion-del-correo.md`.

## What Changes

- Migración `0008`: `users.email_verified_at`, *backfill* con `created_at`, restricción `ck_users_active_requires_verified_email` y tabla `email_verification`.
- Modelos `UserModel.email_verified_at` y `EmailVerificationModel`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `user-persistence`: correo validado y tokens de validación.

## Impact

- `apps/api` (migración `0008`, modelos). Sin cambios en el contrato.
