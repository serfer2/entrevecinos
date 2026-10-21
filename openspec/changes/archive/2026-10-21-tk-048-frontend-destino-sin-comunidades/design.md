## Context

`GET /v1/users/me/memberships` (TK-015) acepta `status` y devuelve las comunidades desactivadas si la membresía está aprobada.

## Decisions

- **`postLoginPath(token)` en `features/auth/destination.ts`:** llama a la API con el token recién emitido en lugar de con la *cookie* que `login` acaba de escribir.
- **Solo cuentan las membresías aprobadas de comunidades activas** (`?status=approved` y `community.is_active`): con una solicitud pendiente el usuario va a `/comunidades`, donde ve su estado.
- **`next` tiene prioridad** y la consulta solo se hace sin él.
- **API caída → `/inicio`:** la sesión ya está creada; el inicio de sesión no falla por esto.
- **`signup` no consulta las membresías:** una cuenta recién creada no tiene ninguna.

## Risks / Trade-offs

- [Una petición más al iniciar sesión sin `next`] → aceptable; solo se hace en ese caso.
