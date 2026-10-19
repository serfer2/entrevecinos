## Why

HU-01 necesita un formulario de registro con errores por campo que deje al vecino dentro de la aplicación con la sesión iniciada. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-01-registrarme-con-mi-correo-electronico/TK-007-frontend-formulario-de-registro.md`.

## What Changes

- Cliente de la API para el servidor de Next (`lib/api/server.ts`, `lib/api/errors.ts`).
- Sesión en la *cookie* `httpOnly` `ev_session` (`features/auth/session.ts`).
- Esquema `signupSchema` (zod), *Server Action* `signup` y `SignupForm`; página `/registro`.
- Página marcador privada `/inicio`.
- Componente compartido `TextField` (etiqueta, ayuda y error accesibles), reutilizable por los formularios de TK-009 y TK-011.
- Vitest + Testing Library (`npm run test`); `@types/node` pasa a `^22` (lo exige Vitest 5; la imagen ya usa Node 22).

## Capabilities

### New Capabilities
- `web-signup`: registro desde el navegador con validación en servidor, errores por campo y sesión en *cookie* `httpOnly`.

### Modified Capabilities

## Impact

- `apps/web` (código, dependencias, configuración de Vitest, README).
