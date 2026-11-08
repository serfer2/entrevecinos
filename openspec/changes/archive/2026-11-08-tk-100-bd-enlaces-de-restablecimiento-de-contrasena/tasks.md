## 1. Base de datos

- [x] 1.1 Modelo `PasswordResetModel` y columna `password_changed_at` en `UserModel`
- [x] 1.2 Migración `0011` revisada a mano, con `downgrade()`
- [x] 1.3 Pruebas `db`: borrado en cascada, cuentas existentes intactas y migración reversible

## 2. Documentación

- [x] 2.1 `readme.md` §3.1 (diagrama) y §3.2 (descripción y tabla de alcance)

## 3. Verificación

- [x] 3.1 `make ci-api` (pruebas, `ruff` y `alembic check`)
