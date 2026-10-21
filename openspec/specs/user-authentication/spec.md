# user-authentication Specification

## Purpose
Inicio de sesión (`POST /v1/auth/token`), validación del token de acceso y usuario autenticado (`GET /v1/users/me`).
## Requirements
### Requirement: Inicio de sesión
`POST /v1/auth/token` SHALL validar `email` (normalizado) y `password`, y responder `200` con `AuthResponse` si son correctos.

#### Scenario: Credenciales correctas
- **WHEN** se envía el correo de una cuenta activa, con cualquier combinación de mayúsculas, y su contraseña
- **THEN** la respuesta es `200` y el `access_token` permite llamar a `GET /v1/users/me`

### Requirement: Error genérico de credenciales
El inicio de sesión MUST responder `401` con `detail: "Correo o contraseña incorrectos."`, idéntico en estado y cuerpo, si el correo no existe, la contraseña no coincide o la cuenta está desactivada o eliminada.

#### Scenario: Cuatro causas, misma respuesta
- **WHEN** se intenta iniciar sesión con un correo inexistente, una contraseña incorrecta, una cuenta desactivada o una eliminada
- **THEN** las cuatro respuestas son iguales

### Requirement: Endpoints protegidos
Los endpoints protegidos MUST responder `401` con `detail: "Autenticación requerida."` y `WWW-Authenticate: Bearer` si falta el token, el esquema no es `Bearer`, el token está mal formado, mal firmado, caducado, usa un algoritmo distinto de HS256, o el usuario no existe, está desactivado o eliminado.

#### Scenario: Token no válido
- **WHEN** se llama a `GET /v1/users/me` con un token caducado o con `alg: none`
- **THEN** la respuesta es `401` con la cabecera `WWW-Authenticate: Bearer`

### Requirement: Usuario actual
`GET /v1/users/me` SHALL devolver el esquema `User` del usuario autenticado, sin datos de contraseña.

#### Scenario: Token válido
- **WHEN** se llama con un token válido
- **THEN** la respuesta es `200` con los datos del usuario y `avatar_url: null`

### Requirement: Correo sin validar
Con la contraseña correcta, `POST /v1/auth/token` MUST responder `403` con `detail: "Tienes que validar tu correo electrónico antes de iniciar sesión."` y `code: "email_not_verified"` si la cuenta no ha validado su correo y no tiene rol `platform_admin`. Con la contraseña incorrecta, la respuesta SHALL seguir siendo el `401` genérico.

#### Scenario: Cuenta sin validar
- **WHEN** una cuenta `user` sin validar inicia sesión con su contraseña
- **THEN** la respuesta es `403` con `code: "email_not_verified"`

#### Scenario: Administrador de plataforma sin validar
- **WHEN** una cuenta `platform_admin` activa sin validar inicia sesión
- **THEN** la respuesta es `200`
