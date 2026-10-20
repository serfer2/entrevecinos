## Why

HU-01 pide crear una cuenta con nombre, correo y contraseña y entrar con la sesión iniciada. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-01-registrarme-con-mi-correo-electronico/TK-006-backend-registro-de-usuario.md`.

## What Changes

- Dominio `users` (entidad `User`, `PlatformRole`, `normalize_email`, `EmailAlreadyRegistered`).
- Puertos `UserRepository`, `PasswordHasher`, `TokenIssuer` y caso de uso `RegisterUser`.
- Adaptadores: repositorio SQLAlchemy, hasher Argon2id (`pwdlib`) y emisor JWT HS256 (`pyjwt`).
- `POST /v1/auth/register` (201/409/422) y manejador de 422 sin `input`.
- `JWT_SECRET` (obligatoria, ≥32) y `JWT_TTL_SECONDS` en configuración, `.env.example` y Compose.

## Capabilities

### New Capabilities
- `user-registration`: registro de cuentas con correo y contraseña, emisión del token de acceso y errores del contrato.

### Modified Capabilities

## Impact

- `apps/api` (cuatro capas, dependencias, pruebas), `.env.example`, `infra/docker-compose.yml`, `apps/api/README.md`.
