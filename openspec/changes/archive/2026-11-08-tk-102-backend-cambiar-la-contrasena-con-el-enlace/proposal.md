## Why

HU-42 (Épica 14): con TK-101 el vecino recibe un enlace de un solo uso, pero todavía no puede cambiar la contraseña con él. Además, los JWT duran 24 horas y no se pueden revocar: si alguien conocía la contraseña antigua y tiene una sesión abierta, debe perderla al cambiarla. Ticket: `docs/product/tickets/EP-14-recuperacion-de-la-contrasena/HU-42-elegir-una-contrasena-nueva-con-el-enlace-recibido/TK-102-backend-cambiar-la-contrasena-con-el-enlace.md`.

## What Changes

- **`POST /v1/auth/password-reset/confirm`** (público): con un enlace válido y una contraseña de 12 a 128 caracteres, cambia la contraseña y responde `204` sin iniciar sesión. `410 password_reset_expired` si el enlace ha caducado; `400 password_reset_invalid` si no existe, ya se usó, se sustituyó o la cuenta ya no puede usarlo; `422` sin consumir el enlace.
- **Cambio de contraseña:** hash nuevo, `users.password_changed_at` (`statement_timestamp()`), enlaces del usuario borrados y, si el correo estaba sin validar, cuenta validada y activa.
- **Sesiones anteriores cerradas:** `JwtTokenService.decode` devuelve también `iat`, y `GetCurrentUser` responde `401` a un JWT emitido antes de `password_changed_at` (truncado al segundo).
- **Aviso por correo** «Tu contraseña de EntreVecinos ha cambiado», con fecha y hora de Madrid. Consume una plaza del cupo; sin cupo, la contraseña cambia igual y el aviso no se envía.
- **Contrato:** `confirmPasswordReset` con `x-mvp: true`, esquemas `PasswordResetConfirmRequest` y `PasswordResetError`; `docs/api/README.md`.
- **`readme.md` §2.5:** recuperación de la contraseña y cierre de sesiones en las medidas de seguridad.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `password-reset`: cambiar la contraseña con el enlace y avisar del cambio.
- `user-authentication`: los JWT emitidos antes del último cambio de contraseña dejan de valer.

## Impact

- API: entidad `User` (`password_changed_at`), errores de dominio, puertos (`change_password`, `delete_for_user`, `TokenClaims`), repositorios SQLAlchemy, `JwtTokenService`, `GetCurrentUser`, caso de uso `ResetPassword`, endpoint, esquemas, manejadores de errores y dependencias; pruebas.
- Contrato: `docs/api/` (ruta, dos esquemas, README). El extracto del `readme.md` no cambia.
- Web: sin cambios (TK-104). La web ya trata el `401` como sesión caducada.
