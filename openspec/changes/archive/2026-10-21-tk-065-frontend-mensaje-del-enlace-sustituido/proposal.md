## Why

HU-27: sin sesión, un enlace sustituido por un reenvío lleva a «Tu correo ya está validado. Inicia sesión.» aunque la cuenta siga pendiente. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-27-entender-por-que-no-funciona-un-enlace-de-validacion-antiguo/TK-065-frontend-mensaje-del-enlace-sustituido.md`.

## What Changes

- `/verificar-correo` decide el destino de un `400` por su `code` (`errorCodeOf`).
- `/verificar-correo/error`: motivo `reemplazado` con el reenvío.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-email-verification`: destino por motivo y página del enlace sustituido.

## Impact

- `apps/web` (`app/verificar-correo`), `apps/web/README.md`.
