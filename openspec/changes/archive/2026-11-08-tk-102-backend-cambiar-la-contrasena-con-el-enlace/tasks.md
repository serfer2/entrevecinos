## 1. Dominio y puertos

- [x] 1.1 `User.password_changed_at`, errores `PasswordResetInvalid` y `PasswordResetExpired`, `TokenClaims`, `UserRepository.change_password` y `PasswordResetRepository.delete_for_user`

## 2. Sesiones

- [x] 2.1 `JwtTokenService.decode` con `iat` y regla en `GetCurrentUser`, con pruebas unitarias

## 3. Caso de uso y endpoint

- [x] 3.1 Repositorios SQLAlchemy (`change_password`, `delete_for_user`, `password_changed_at` en el dominio), con pruebas `db`
- [x] 3.2 `ResetPassword` y aviso del cambio, con pruebas unitarias
- [x] 3.3 Endpoint `POST /v1/auth/password-reset/confirm`, esquemas, manejadores y dependencias, con pruebas de endpoint (cambio, errores, sesiones, cuenta sin validar, cupo)

## 4. Contrato y documentación

- [x] 4.1 `docs/api/paths/auth_password_reset_confirm.yaml`, esquemas, `openapi.yaml` y `docs/api/README.md`; lint
- [x] 4.2 `readme.md` §2.5

## 5. Verificación

- [x] 5.1 `make ci-api` y prueba local con Mailpit
