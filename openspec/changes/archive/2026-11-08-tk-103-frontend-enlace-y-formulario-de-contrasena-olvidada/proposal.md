## Why

HU-41 AC1 y AC3 (Épica 14): la pantalla de inicio de sesión no ofrece ninguna salida a quien ha olvidado su contraseña. La API ya envía el enlace (`POST /v1/auth/password-reset`, TK-101). Ticket: `docs/product/tickets/EP-14-recuperacion-de-la-contrasena/HU-41-pedir-un-enlace-para-restablecer-mi-contrasena/TK-103-frontend-enlace-y-formulario-de-contrasena-olvidada.md`.

## What Changes

- **Inicio de sesión:** enlace «¿Has olvidado tu contraseña?» a `/recuperar-contrasena`; tras un intento fallido, con el correo escrito en `?email=`.
- **Página pública `/recuperar-contrasena`:** «Recupera tu contraseña», campo de correo y botón «Enviar enlace». Con sesión, redirige a `/inicio`.
- **Server Action `requestPasswordReset`:** `202` → aviso que no revela si el correo tiene cuenta; `503 email_quota_exceeded` → mensaje de cupo; `422` → error en el campo; otro error → mensaje genérico. Conserva el correo.
- **Ruta pública** en `PUBLIC_ROUTES`.

## Capabilities

### New Capabilities
- `web-password-reset`: recuperación de la contraseña en la web.

### Modified Capabilities
- (ninguna)

## Impact

- Web: `features/auth` (`routes.ts`, `schemas.ts`, `actions.ts`, `LoginForm`, nuevo `PasswordResetRequestForm`), página `app/recuperar-contrasena/page.tsx`; pruebas.
- Sin cambios en la API ni en la infraestructura (los límites por IP del proxy, en TK-105).
