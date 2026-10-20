## ADDED Requirements

### Requirement: Filtros por tipo y categoría
`GET /v1/communities/{community_id}/listings` SHALL aceptar `type` (un `ListingType`) y `category_id` (UUID), combinados con `AND` entre sí y con `q`, y `total` MUST reflejarlos. Un tipo desconocido o un `category_id` mal formado MUST responder `422`; una categoría inexistente devuelve una lista vacía. Los filtros no saltan la regla de acceso.

#### Scenario: Por tipo
- **WHEN** se pide `type=sell`
- **THEN** solo se obtienen anuncios de tipo `sell`

#### Scenario: Combinados
- **WHEN** se pide `q=bici&type=sell`
- **THEN** solo se obtienen los que cumplen ambas condiciones

#### Scenario: Ajeno
- **WHEN** un usuario que no es miembro pide `type=sell`
- **THEN** recibe `403`
