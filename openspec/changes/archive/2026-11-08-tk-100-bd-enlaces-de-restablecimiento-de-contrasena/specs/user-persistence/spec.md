## ADDED Requirements

### Requirement: Enlaces de restablecimiento de contraseña
La tabla `password_reset`, creada por la migración `0011`, SHALL guardar `token_hash` (`CHAR(64)`, PK, SHA-256 del *token*), `user_id` (FK a `users` con `ON DELETE CASCADE`, indexada), `expires_at` y `created_at` (`DEFAULT now()`). El *token* en claro MUST NOT guardarse.

#### Scenario: Borrado del usuario
- **WHEN** se borra un usuario con enlaces de restablecimiento
- **THEN** sus enlaces desaparecen

#### Scenario: Migración reversible
- **WHEN** se revierte `0011` y se vuelve a aplicar
- **THEN** la tabla `password_reset` y la columna `users.password_changed_at` desaparecen y vuelven sin errores

### Requirement: Fecha del último cambio de contraseña
La tabla `users` SHALL tener la columna `password_changed_at` (`TIMESTAMPTZ NULL`). La migración MUST dejarla nula en las cuentas existentes, sin cambiar su contraseña.

#### Scenario: Cuentas existentes
- **WHEN** se aplica `0011` sobre una base con usuarios
- **THEN** todos conservan su `password_hash` y tienen `password_changed_at` nulo

### Requirement: Entidad del MVP documentada
El modelo de datos del `readme.md` (§3.1 y §3.2) SHALL incluir `password_reset` y `users.password_changed_at`, con `password_reset` marcada como entidad del MVP.

#### Scenario: Consulta del modelo
- **WHEN** se lee la tabla de alcance del modelo de datos del `readme.md`
- **THEN** `password_reset` figura con alcance MVP
