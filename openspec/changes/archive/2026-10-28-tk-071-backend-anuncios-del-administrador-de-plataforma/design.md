## Context

`require_member` ya deja pasar a un `platform_admin`; el filtro del listado no.

## Decisions

- **`EXISTS` sobre un alias propio de `users`:** la consulta exterior ya une `users` y el subselect no debe correlacionarse con ella.
- **Misma regla en listado, búsqueda, `total` y detalle** (`owner_is_member`).

## Risks / Trade-offs

- [Un `platform_admin` bloqueado en una comunidad sigue mostrando sus anuncios] → coherente con `require_member`.
