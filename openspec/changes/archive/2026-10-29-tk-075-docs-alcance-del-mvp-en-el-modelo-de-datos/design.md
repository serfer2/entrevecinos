## Context

| Alcance | Entidades |
|---|---|
| MVP (tabla en `infrastructure/db/models/`) | `user` (`users`), `email_verification`, `community`, `community_membership`, `category`, `listing`, `media_asset`, `listing_image` |
| Versión futura | `conversation`, `message`, `notification`, `professional_profile`, `professional_service`, `professional_profile_image`, `report` |

## Decisions

- **Marca en el texto, no en estilos:** `erDiagram` no admite estilos por entidad (asumido); «Versión futura» va en el comentario del primer atributo (el `id`, o la clave compuesta de `professional_profile_image`) y en una nota bajo el diagrama.
- **Tabla entidades ↔ rutas en §3.2:** es el punto de cruce entre el modelo y el contrato; las rutas se copian del contrato tras TK-074.
- **Campos sin uso en el MVP** (p. ej. `users.avatar_asset_id`) se documentan como están.

## Risks / Trade-offs

- [Diagrama ER más cargado] → renderizar con `mermaid-cli`.
