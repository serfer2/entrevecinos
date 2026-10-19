## 1. Configuración

- [x] 1.1 Dependencias `pwdlib[argon2]`, `pyjwt`, `pydantic[email]`; regenerar `uv.lock`
- [x] 1.2 `JWT_SECRET` y `JWT_TTL_SECONDS` en `Settings`, `.env.example` y Compose

## 2. Dominio y aplicación

- [x] 2.1 `domain/users`: `User`, `NewUser`, `PlatformRole`, `normalize_email`, `EmailAlreadyRegistered`
- [x] 2.2 `application/users`: puertos, `AccessToken`, `RegisterUser` y pruebas unitarias con fakes

## 3. Infraestructura

- [x] 3.1 `SqlAlchemyUserRepository` (`get_by_email`, `add` con savepoint)
- [x] 3.2 `Argon2PasswordHasher` y `JwtTokenService.issue()`

## 4. Presentación

- [x] 4.1 Esquemas `RegisterRequest`, `UserResponse`, `AuthResponse`
- [x] 4.2 Dependencias y router `POST /v1/auth/register`
- [x] 4.3 Manejadores de `EmailAlreadyRegistered` (409) y `RequestValidationError` (422 sin `input`)

## 5. Pruebas y verificación

- [x] 5.1 Pruebas de integración del endpoint (AC1–AC4) y de configuración (AC5)
- [x] 5.2 Ampliar `test_architecture.py` con `pwdlib`, `jwt`, `email_validator`
- [x] 5.3 Actualizar `apps/api/README.md` y verificar según TK-006 §6
