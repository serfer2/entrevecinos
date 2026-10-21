## Context

TK-050 crea todas las comunidades inactivas.

## Decisions

- **`CreateCommunity.execute(community, creator: User)`:** el caso de uso decide `is_active` con el rol de plataforma del creador, en lugar de recibir el valor desde la presentación.
- **El `platform_admin` sigue quedando como `community_admin` aprobado** de la comunidad que crea.

## Risks / Trade-offs

- Ninguno relevante.
