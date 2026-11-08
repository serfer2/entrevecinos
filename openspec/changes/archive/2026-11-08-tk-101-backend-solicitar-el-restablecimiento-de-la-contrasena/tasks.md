## 1. Aplicación e infraestructura

- [x] 1.1 Entidad `PasswordReset`, `User.can_reset_password` y puerto `PasswordResetRepository`
- [x] 1.2 `SqlAlchemyPasswordResetRepository` con pruebas `db`
- [x] 1.3 `PasswordResetIssuer` (enlace, caducidad y mensaje) y `RequestPasswordReset`, con pruebas unitarias

## 2. Presentación

- [x] 2.1 Ajuste `PASSWORD_RESET_TTL_MINUTES`, dependencias, esquemas y endpoint `POST /v1/auth/password-reset`, con pruebas de endpoint (cuentas, límite de un minuto y cupo)

## 3. Contrato y documentación

- [x] 3.1 `docs/api/paths/auth_password_reset.yaml`, esquemas, `openapi.yaml`, tabla de cambios y resumen de `docs/api/README.md`; lint y bundle
- [x] 3.2 `.env.example` y `apps/api/README.md`

## 4. Verificación

- [x] 4.1 `make ci-api` y prueba local con Mailpit
