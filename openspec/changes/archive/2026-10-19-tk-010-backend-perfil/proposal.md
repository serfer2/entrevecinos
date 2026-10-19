## Why

HU-03 pide editar el nombre y el teléfono, con el nombre obligatorio. Ticket de origen: `docs/product/tickets/EP-01-registro-y-perfil-basico/HU-03-gestionar-mi-perfil-y-datos-de-contacto/TK-010-backend-actualizar-perfil.md`.

## What Changes

- `PATCH /v1/users/me`: actualización parcial de `full_name` y `phone` del usuario autenticado.
- Caso de uso `UpdateProfile` (`ProfileChanges` distingue «no enviado» de `null`) y `UserRepository.update_profile()`.
- `updated_at` se actualiza con `statement_timestamp()` (en lugar de `now()`, que devuelve el inicio de la transacción).
- Diferencia temporal con el contrato: `avatar_asset_id`, `password` y `current_password` se rechazan con `422`.

## Capabilities

### New Capabilities
- `user-profile`: edición del perfil propio (nombre y teléfono).

### Modified Capabilities

## Impact

- `apps/api` (aplicación, infraestructura, presentación y pruebas).
