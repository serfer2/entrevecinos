# user-persistence Specification

## Purpose
Persistencia de usuarios en PostgreSQL (tabla `users`) con SQLAlchemy y migraciones Alembic.
## Requirements
### Requirement: Tabla de usuarios
La base de datos SHALL contener la tabla `users` y el enum `user_role` (`user`, `platform_admin`) creados por la migración `0001_create_users`, con las columnas, tipos, valores por defecto y restricciones definidos en TK-005 §3.5.

#### Scenario: Migración aplicada
- **WHEN** se levanta el entorno con `make dev`
- **THEN** `\d users` muestra la tabla con sus restricciones y `alembic current` indica `0001 (head)`

### Requirement: Migraciones reversibles
Cada migración MUST incluir `downgrade()` y SHALL poder revertirse y volver a aplicarse sin errores.

#### Scenario: Downgrade y upgrade
- **WHEN** se ejecuta `alembic downgrade base` y después `alembic upgrade head`
- **THEN** ambos comandos terminan sin errores y la tabla `users` vuelve a existir

### Requirement: Correo único y en minúsculas
La tabla `users` MUST rechazar correos duplicados (`UNIQUE`) y correos con mayúsculas (`CHECK (email = lower(email))`).

#### Scenario: Correo duplicado
- **WHEN** se inserta un segundo usuario con `vecino@example.com`
- **THEN** la base de datos lo rechaza por `uq_users_email`

#### Scenario: Correo con mayúsculas
- **WHEN** se inserta un usuario con `Vecino@Example.com`
- **THEN** la base de datos lo rechaza por la restricción de minúsculas

### Requirement: Valores por defecto
Una inserción con solo `email`, `password_hash` y `full_name` SHALL generar `id`, `platform_role = 'user'`, `is_active = true`, `created_at` y `updated_at`, y dejar nulos `phone`, `avatar_asset_id` y `deleted_at`.

#### Scenario: Inserción mínima
- **WHEN** se inserta un usuario con los tres campos obligatorios
- **THEN** la fila leída tiene los valores por defecto indicados

### Requirement: Pruebas aisladas
Las pruebas de integración SHALL ejecutarse contra `<db>_test`, creada automáticamente, y MUST NOT modificar la base de datos de desarrollo.

#### Scenario: pytest con datos de desarrollo
- **WHEN** se ejecuta `pytest` con datos en la base de datos de desarrollo
- **THEN** las pruebas pasan y la base de datos de desarrollo no cambia

### Requirement: Correo validado
La tabla `users` SHALL tener `email_verified_at TIMESTAMPTZ NULL` y la restricción `ck_users_active_requires_verified_email`, que MUST rechazar una cuenta activa sin correo validado salvo con rol `platform_admin`. La migración `0008` SHALL dar por validadas las cuentas existentes (`email_verified_at = created_at`).

#### Scenario: Cuenta activa sin validar
- **WHEN** se guarda una cuenta `user` con `is_active = true` y `email_verified_at` nulo
- **THEN** la base de datos la rechaza por `ck_users_active_requires_verified_email`

#### Scenario: Administrador de plataforma sin validar
- **WHEN** se guarda una cuenta `platform_admin` activa con `email_verified_at` nulo
- **THEN** se acepta

### Requirement: Tokens de validación
La tabla `email_verification` SHALL guardar `token_hash` (`CHAR(64)`, PK, SHA-256 del token), `user_id` (FK a `users` con `ON DELETE CASCADE`, indexada), `expires_at` y `created_at`. El token en claro MUST NOT guardarse.

#### Scenario: Borrado del usuario
- **WHEN** se borra un usuario con tokens de validación
- **THEN** sus tokens desaparecen
