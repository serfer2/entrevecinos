## Why

HU-27: emitir un enlace nuevo borra los anteriores y validar el correo borra todos, así que la API no puede distinguir un enlace sustituido de uno usado o de uno que nunca existió. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-27-entender-por-que-no-funciona-un-enlace-de-validacion-antiguo/TK-063-bd-enlaces-usados-y-sustituidos.md`.

## What Changes

- Migración `0009`: `email_verification.used_at` y `superseded_at`, restricción `ck_email_verification_used_or_superseded` e índice único parcial `uq_email_verification_one_active_per_user`.
- Repositorio: `replace` marca los anteriores como sustituidos y purga los caducados hace más de 30 días; `mark_used` sustituye a `delete_for_user`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `user-persistence`: enlaces usados y sustituidos.

## Impact

- `apps/api` (migración `0009`, modelo, entidad, repositorio y *fake*), `readme.md` (modelo de datos). Sin cambios en el contrato.
