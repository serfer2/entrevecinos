## Why

HU-27: `POST /auth/email-verification` responde el mismo `400 verification_invalid` para un token desconocido, usado o sustituido, y la web no puede dar el mensaje correcto. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-27-entender-por-que-no-funciona-un-enlace-de-validacion-antiguo/TK-064-backend-motivo-del-enlace-no-valido.md`.

## What Changes

- `VerifyEmail` comprueba, en orden: token o usuario inexistente → `verification_invalid`; cuenta validada → `email_already_verified`; sustituido → `verification_superseded` con `email`; caducado → `410`. Al validar, `mark_used`.
- Errores de dominio `EmailAlreadyVerified` y `VerificationSuperseded`, con sus manejadores.
- Contrato: `VerificationError.code` con los valores nuevos y ejemplos del `400`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `email-verification`: motivo del enlace no válido.

## Impact

- `apps/api` (área `users`), `docs/api` (compatible), `apps/api/README.md`.
