## Context

TK-005 fijó las convenciones (UUID con `gen_random_uuid()`, `TIMESTAMPTZ`, nombres de restricciones por `NAMING_CONVENTION`).

## Goals / Non-Goals

**Goals:** esquema de §3 del ticket, restricciones en la base de datos, migración reversible.

**Non-Goals:** dominio, casos de uso y endpoints (TK-013 y siguientes).

## Decisions

- **PK compuesta `(community_id, user_id)`:** garantiza una membresía por par sin índice extra.
- **`CHECK (status <> 'approved' OR joined_at IS NOT NULL)`** (`ck_community_membership_approved_has_joined_at`).
- **FK con `ON DELETE`:** `created_by` RESTRICT, membresías CASCADE, `reviewed_by` SET NULL.
- **Enums nativos de PostgreSQL** como `user_role`; el `downgrade()` los elimina.

## Risks / Trade-offs

- [Cambiar valores de enum requiere migración] → aceptable; los valores salen del modelo de datos.
