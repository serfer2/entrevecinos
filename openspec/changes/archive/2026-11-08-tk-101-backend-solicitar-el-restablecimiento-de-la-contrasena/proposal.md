## Why

HU-41 (Épica 14): quien olvida su contraseña no tiene forma de recuperar su cuenta. La tabla `password_reset` ya existe (TK-100); falta el endpoint que envía el enlace por correo sin revelar qué correos están registrados y sin permitir abusos. Ticket: `docs/product/tickets/EP-14-recuperacion-de-la-contrasena/HU-41-pedir-un-enlace-para-restablecer-mi-contrasena/TK-101-backend-solicitar-el-restablecimiento-de-la-contrasena.md`.

## What Changes

- **`POST /v1/auth/password-reset`** (público): siempre `202` con el mismo mensaje, exista o no la cuenta; `503 email_quota_exceeded` sin cupo, comprobado antes de buscar la cuenta; `422` con un cuerpo no válido.
- **Enlace de un solo uso** `{WEB_PUBLIC_URL}/restablecer-contrasena/enlace?token=…`, válido `PASSWORD_RESET_TTL_MINUTES` (60); solo se guarda su SHA-256 y pedir otro borra los anteriores.
- **Como mucho un enlace por minuto** para cada cuenta; cada envío consume una plaza del cupo de correos.
- **Cuentas que reciben el enlace:** activas y pendientes de validar el correo. Las borradas o desactivadas con el correo validado no reciben nada.
- **Contrato:** `requestPasswordReset` con `x-mvp: true`, esquemas `PasswordResetRequest` y `PasswordResetRequested`; tabla de cambios y resumen de `docs/api/README.md`.

## Capabilities

### New Capabilities
- `password-reset`: recuperación de la contraseña olvidada mediante un enlace por correo.

### Modified Capabilities
- (ninguna)

## Impact

- API: puerto `PasswordResetRepository` y adaptador SQLAlchemy, `PasswordResetIssuer`, caso de uso `RequestPasswordReset`, endpoint, esquemas y dependencias; ajuste en `Settings`; pruebas.
- Contrato: `docs/api/` (ruta, dos esquemas, README). El extracto del `readme.md` no cambia (no incluye esta operación).
- Configuración: `.env.example` y `apps/api/README.md`. El Compose de producción, en TK-105 (el valor por defecto ya es 60).
