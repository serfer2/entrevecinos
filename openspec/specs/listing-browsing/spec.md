# listing-browsing Specification

## Purpose
Listado, búsqueda, filtros y orden de los anuncios de una comunidad.
## Requirements
### Requirement: Listado de anuncios de la comunidad
`GET /v1/communities/{community_id}/listings` SHALL devolver a los miembros aprobados `Page[Listing]` con los anuncios `active` y `reserved` no eliminados de esa comunidad, del más reciente al más antiguo (`published_at DESC`, `id DESC`).

#### Scenario: Orden por defecto
- **WHEN** hay anuncios publicados en fechas distintas
- **THEN** aparecen del más reciente al más antiguo

#### Scenario: Comunidad sin anuncios
- **WHEN** no hay anuncios visibles
- **THEN** la respuesta es `200` con `items: []` y `total: 0`

#### Scenario: Estados no visibles
- **WHEN** hay anuncios `hidden`, `completed`, `draft` o eliminados
- **THEN** no aparecen en el listado ni en `total`

### Requirement: Acceso restringido al listado
Quien no es miembro aprobado MUST recibir `403` (con `status` si tiene membresía); una comunidad inexistente `404`.

#### Scenario: Pendiente
- **WHEN** un usuario con la solicitud pendiente pide el listado
- **THEN** recibe `403` con `status: "pending"`

### Requirement: Sin N+1
El listado SHALL ejecutar un número fijo de sentencias SQL, independiente del número de anuncios e imágenes.

#### Scenario: Diez anuncios con tres imágenes
- **WHEN** se lista una página con 10 anuncios de 3 imágenes
- **THEN** se ejecutan las mismas sentencias que con un anuncio

