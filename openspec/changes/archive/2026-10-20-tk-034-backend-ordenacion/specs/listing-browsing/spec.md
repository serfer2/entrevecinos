## ADDED Requirements

### Requirement: Ordenación del listado
`GET /v1/communities/{community_id}/listings` SHALL ordenar por `sort` (`published_at` por defecto, o `price`) en la dirección `order` (`desc` por defecto, o `asc`), con desempate estable entre páginas; al ordenar por precio, los anuncios sin precio MUST aparecer al final en ambos sentidos. Valores fuera del enum MUST responder `422`.

#### Scenario: Por fecha
- **WHEN** se pide `sort=published_at&order=desc` y después `order=asc`
- **THEN** se obtiene del más reciente al más antiguo, y al revés

#### Scenario: Por precio con anuncios sin precio
- **WHEN** se pide `sort=price` en cualquier sentido
- **THEN** los anuncios con precio aparecen ordenados y los sin precio al final

#### Scenario: Campo no permitido
- **WHEN** se pide `sort=title`
- **THEN** la respuesta es `422`
