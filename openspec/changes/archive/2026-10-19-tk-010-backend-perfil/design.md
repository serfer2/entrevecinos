## Context

TK-008 dejó `get_current_user` y `GET /v1/users/me`. Contrato: `users_me.yaml` (`patch`), `UserUpdate.yaml`.

## Goals / Non-Goals

**Goals:** actualización parcial atómica; validaciones de §3.2 del ticket; sin cambios ante cualquier error.

**Non-Goals:** avatar, contraseña, correo.

## Decisions

- **`ProfileChanges` con centinela `UNSET`:** `phone=None` borra el teléfono; `UNSET` lo deja intacto. Se construye desde `model_fields_set`.
- **El repositorio recibe solo los campos enviados** (`ProfileChanges.as_values()`), los aplica al modelo ORM y hace `flush` + `refresh`; la sesión por petición confirma o revierte todo.
- **`full_name: null` explícito → 422:** validador `before` (los valores por defecto no se validan, así que «no enviado» sigue siendo válido).
- **Cuerpo vacío → 422** con un validador `after` sobre `model_fields_set` (equivale a `minProperties: 1`).
- **`onupdate=func.statement_timestamp()`:** `now()` es el inicio de la transacción; con `statement_timestamp()` `updated_at` refleja el momento real del cambio. Solo afecta al ORM (sin migración).

## Risks / Trade-offs

- [El contrato publicado admite campos que la API rechaza] → documentado en la descripción del endpoint hasta sus tickets.
