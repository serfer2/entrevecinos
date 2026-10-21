## Why

HU-26: el usuario necesita pedir otro correo de validación al registrarse con un correo pendiente, con un enlace caducado y al iniciar sesión sin validar. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-26-recibir-de-nuevo-el-correo-de-validacion/TK-061-frontend-reenvio-del-correo-de-validacion.md`.

## What Changes

- *Server Action* `resendVerification` y componente `ResendVerificationButton`.
- `/registro`: «Este correo está pendiente de validación.» con el botón (`409 email_pending_verification`).
- `/verificar-correo/error?motivo=caducado`: el botón con el `email` de la URL; sin él, enlace a `/registro`.
- `/iniciar-sesion`: el botón bajo el mensaje de correo sin validar.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-email-verification`: reenvío del correo de validación.

## Impact

- `apps/web` (`features/auth`, `app/registro`, `app/iniciar-sesion`, `app/verificar-correo/error`).
