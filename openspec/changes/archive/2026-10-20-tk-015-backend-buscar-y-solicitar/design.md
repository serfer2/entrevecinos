## Context

TK-012/TK-013 dejaron las tablas, `CommunityRepository` y `NotFoundError`. Contrato: `communities.yaml` (`get`), `communities_community_id_memberships.yaml` (`post`), `users_me_memberships.yaml`, `Membership`, `MyMembership`, `PageMeta`.

## Goals / Non-Goals

**Goals:** paginación reutilizable; búsqueda insensible a mayúsculas y tildes; solicitud idempotente frente a duplicados.

**Non-Goals:** aprobar o rechazar (TK-017); bloqueo (TK-040).

## Decisions

- **`f_unaccent(text)` inmutable** envolviendo `unaccent('unaccent', $1)`, para poder indexarla en el futuro (`pg_trgm`).
- **Escape de `%`, `_` y `\`** del texto del usuario y `LIKE ... ESCAPE '\'`.
- **Duplicados:** se consulta antes y, además, la violación de la PK (`pk_community_membership`) en un *savepoint* se traduce a `MembershipAlreadyExists(status)` (carreras).
- **Lecturas con datos relacionados** (`MembershipDetail` con el nombre del usuario, `MyMembership` con la comunidad) en una sola consulta con `JOIN`.
- **`MyMembership` de comunidades desactivadas** solo si la membresía está aprobada.

## Risks / Trade-offs

- [`LIKE '%…%'` sin índice] → suficiente para el MVP; índice de trigramas si crece.
- [Un rechazo es definitivo: el `409` responde en cualquier estado] → documentado en el ticket.
