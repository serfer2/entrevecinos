## Context

TK-005 dejó la tabla `users` y `get_session()`. Detalle del contrato en TK-006 §3.4.

## Goals / Non-Goals

**Goals:** registro conforme a `auth_register.yaml`; hash Argon2id; token JWT con `sub`, `iat`, `exp`; 422 sin datos sensibles.

**Non-Goals:** login, validación de tokens, `/users/me` (TK-008); verificación de correo; limitación de peticiones.

## Decisions

- **`NewUser` + `User`:** el repositorio recibe un `NewUser` (sin id) y el *hash* por separado, y devuelve el `User` persistido con los valores por defecto de la base de datos (`id`, `created_at`). Así `User` nunca lleva el *hash*.
- **Duplicados por restricción:** `add()` hace `flush` dentro de un *savepoint* (`begin_nested`) y traduce la violación de `uq_users_email` a `EmailAlreadyRegistered`. La comprobación previa con `get_by_email` da el error rápido; la restricción cubre la carrera entre peticiones simultáneas.
- **Transacción por petición:** `get_session()` confirma al terminar la petición; el token se emite antes del `commit`, pero cualquier violación aflora en el `flush`, así que no se emite token para una cuenta que no llega a crearse.
- **Errores de dominio → HTTP en `presentation`:** manejador de excepciones registrado en `create_app()`.
- **Manejador de `RequestValidationError`:** devuelve `{"detail": [{loc, msg, type}]}`; descarta `input` y `ctx`.
- **Pruebas de integración:** la fixture `client` sobrescribe `get_session` con la `db_session` transaccional de TK-005.

## Risks / Trade-offs

- [El 409 permite enumerar cuentas] → exigido por HU-01; limitación de peticiones en un ticket posterior.
- [Argon2id ralentiza las pruebas] → coste aceptable (decenas de ms por hash).
