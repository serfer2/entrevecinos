## Why

HU-41 y HU-42 (Épica 14): quien olvida su contraseña no puede recuperar su cuenta. Para enviar enlaces de restablecimiento de un solo uso hay que guardarlos con su caducidad sin que una copia de la base de datos sirva para usarlos, y para cerrar las sesiones anteriores a un cambio de contraseña hay que saber cuándo cambió. Ticket: `docs/product/tickets/EP-14-recuperacion-de-la-contrasena/HU-41-pedir-un-enlace-para-restablecer-mi-contrasena/TK-100-bd-enlaces-de-restablecimiento-de-contrasena.md`.

## What Changes

- **Tabla `password_reset`** (migración `0011`): `token_hash` (`CHAR(64)`, PK, SHA-256 del *token*), `user_id` (FK a `users`, `ON DELETE CASCADE`, indexada), `expires_at` y `created_at`.
- **Columna `users.password_changed_at`** (`TIMESTAMPTZ NULL`), nula en las cuentas existentes.
- **Modelos SQLAlchemy** `PasswordResetModel` y columna en `UserModel`.
- **Documentación:** `readme.md` §3.1 (diagrama) y §3.2 (descripción y tabla de alcance) con `password_reset` como entidad del MVP.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `user-persistence`: enlaces de restablecimiento de contraseña y fecha del último cambio.

## Impact

- API: `infrastructure/db/models/user.py`, `models/__init__.py`, migración `0011`; pruebas `db`.
- Documentación: `readme.md` §3.1 y §3.2.
- Producción: `deploy.sh` hace copia previa al detectar la migración pendiente; solo añade objetos, compatible con la API anterior.
