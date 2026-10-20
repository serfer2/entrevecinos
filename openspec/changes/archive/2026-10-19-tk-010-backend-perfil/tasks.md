## 1. Aplicación e infraestructura

- [x] 1.1 `ProfileChanges` (`UNSET`) y `UpdateProfile`, con pruebas unitarias
- [x] 1.2 `UserRepository.update_profile()` (puerto, SQLAlchemy y fake)
- [x] 1.3 `UserModel.updated_at` con `onupdate=func.statement_timestamp()`

## 2. Presentación

- [x] 2.1 `UserUpdateRequest` (validaciones de TK-010 §3.2)
- [x] 2.2 `PATCH /v1/users/me` con la diferencia temporal documentada

## 3. Pruebas y verificación

- [x] 3.1 Integración AC1–AC5, datos intactos tras `422`, `updated_at` y `created_at`
- [x] 3.2 Verificación TK-010 §6
