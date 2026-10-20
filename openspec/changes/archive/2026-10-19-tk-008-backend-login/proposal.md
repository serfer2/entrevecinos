## Why

HU-02 pide iniciar sesión con un error genérico y proteger el contenido privado. Falta validar credenciales y tokens. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-02-iniciar-sesion/TK-008-backend-inicio-de-sesion-y-usuario-actual.md`.

## What Changes

- `POST /v1/auth/token`: inicio de sesión con respuesta `401` genérica y tiempo de respuesta constante.
- `JwtTokenService.decode()` y dependencia `get_current_user` (Bearer), base de todos los endpoints protegidos.
- `GET /v1/users/me`.
- Rehash de contraseñas con parámetros antiguos tras un inicio de sesión correcto.

## Capabilities

### New Capabilities
- `user-authentication`: inicio de sesión, validación del token de acceso y consulta del usuario autenticado.

### Modified Capabilities

## Impact

- `apps/api` (dominio, aplicación, infraestructura, presentación y pruebas), `apps/api/README.md`.
