## 1. Dominio y aplicación

- [x] 1.1 `InvalidCredentials`, `NotAuthenticated` y `User.can_authenticate`
- [x] 1.2 Puertos: `get_by_id`, `get_credentials`, `update_password_hash`, `verify_and_update`, `TokenService.decode`
- [x] 1.3 `AuthenticateUser` y `GetCurrentUser`, con pruebas unitarias

## 2. Infraestructura

- [x] 2.1 Repositorio: `get_by_id`, `get_credentials`, `update_password_hash`
- [x] 2.2 `Argon2PasswordHasher.verify_and_update` con hash ficticio
- [x] 2.3 `JwtTokenService.decode`

## 3. Presentación

- [x] 3.1 `LoginRequest`, `POST /v1/auth/token`
- [x] 3.2 `get_current_user` (`bearerAuth`) y `GET /v1/users/me`
- [x] 3.3 Manejadores `401` de `InvalidCredentials` y `NotAuthenticated`

## 4. Pruebas y verificación

- [x] 4.1 Integración de `/auth/token` y `/users/me` (casos de TK-008 §3.5)
- [x] 4.2 README (cómo proteger un endpoint) y verificación TK-008 §6
