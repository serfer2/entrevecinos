## Why

HU-03 pide ver el nombre, el correo y el teléfono y editar el nombre y el teléfono, con el nombre obligatorio. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-03-gestionar-mi-perfil-y-datos-de-contacto/TK-011-frontend-pagina-de-perfil.md`.

## What Changes

- Página privada `/perfil` con los datos guardados (correo de solo lectura) y `ProfileForm`.
- `profileSchema` (zod) y *Server Action* `updateProfile` contra `PATCH /v1/users/me`.
- Enlace «Mi perfil» en `/inicio`.

## Capabilities

### New Capabilities
- `web-profile`: consulta y edición del perfil propio desde el navegador.

### Modified Capabilities

## Impact

- `apps/web` (`features/profile`, `app/(privado)/perfil`, `/inicio`, pruebas).
