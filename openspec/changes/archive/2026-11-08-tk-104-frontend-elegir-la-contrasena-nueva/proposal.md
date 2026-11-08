## Why

HU-42 (Épica 14): el correo de TK-101 lleva a `/restablecer-contrasena/enlace?token=…`, que todavía no existe, y la API ya cambia la contraseña con `POST /v1/auth/password-reset/confirm` (TK-102). Ticket: `docs/product/tickets/EP-14-recuperacion-de-la-contrasena/HU-42-elegir-una-contrasena-nueva-con-el-enlace-recibido/TK-104-frontend-elegir-la-contrasena-nueva.md`.

## What Changes

- **Route handler `/restablecer-contrasena/enlace`:** guarda el *token* en la *cookie* `HttpOnly` `ev_password_reset` (1 hora, solo para `/restablecer-contrasena`) y redirige a `/restablecer-contrasena`, sin el *token* en la URL. No llama a la API. `Referrer-Policy: no-referrer` y `Cache-Control: no-store`.
- **Página `/restablecer-contrasena`:** con la *cookie*, formulario «Contraseña nueva» y «Repite la contraseña»; sin ella o con `motivo=invalido|caducado`, el mensaje y «Pedir otro enlace».
- **Server Action `resetPassword`:** lee el *token* de la *cookie*; `204` → borra la *cookie* y la sesión y lleva a `/iniciar-sesion?motivo=contrasena-cambiada`; `410`/`400` → borra la *cookie* y explica el motivo; `422` → error en el campo; otro error → mensaje genérico.
- **Inicio de sesión:** aviso «Tu contraseña se ha cambiado. Inicia sesión con la nueva.».
- **Rutas públicas** `/restablecer-contrasena` y `/restablecer-contrasena/enlace`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `web-password-reset`: elegir la contraseña nueva desde el enlace del correo.

## Impact

- Web: `features/auth` (`routes.ts`, `schemas.ts`, `actions.ts`, nuevo `reset-token.ts`, `password-reset-link.ts` y `PasswordResetForm`), `app/restablecer-contrasena/` (página y *route handler*), `app/iniciar-sesion/page.tsx`, `next.config.ts` (`Referrer-Policy` de la ruta del enlace); pruebas.
- Sin cambios en la API ni en la CSP.
