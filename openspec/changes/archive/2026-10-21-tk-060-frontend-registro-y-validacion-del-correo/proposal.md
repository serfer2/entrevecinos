## Why

HU-25: con TK-058 el registro ya no devuelve un JWT; la cuenta se activa al abrir el enlace del correo. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-25-validar-mi-correo-electronico-al-registrarme/TK-060-frontend-registro-y-validacion-del-correo.md`.

## What Changes

- `signup` devuelve `{ verificationSentTo }` y `SignupForm` muestra el aviso del correo enviado en lugar de crear la sesión.
- *Route handler* público `GET /verificar-correo`: valida el token, crea la sesión y lleva a `/comunidades`.
- Página pública `/verificar-correo/error` (caducado, no válido, error).
- `login`: mensaje para `403 email_not_verified`; `/iniciar-sesion?motivo=correo-validado`.

## Capabilities

### New Capabilities
- `web-email-verification`: validación del correo desde el enlace.

### Modified Capabilities
- `web-signup`: aviso tras el registro, sin sesión.
- `web-session`: mensaje de correo sin validar y aviso de correo ya validado.

## Impact

- `apps/web` (`features/auth`, `app/registro`, `app/verificar-correo`, `app/iniciar-sesion`, `lib/api/errors.ts`).
