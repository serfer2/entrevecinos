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

### Requirement: Búsqueda por palabras clave
`GET /v1/communities/{community_id}/listings?q=…` SHALL devolver solo los anuncios visibles cuyo título o descripción contienen todas las palabras de `q` (por prefijo, sin distinguir mayúsculas ni tildes), con el `total` correspondiente. Los caracteres especiales MUST NOT provocar errores.

#### Scenario: Coincidencias
- **WHEN** se busca `q=bicicleta`, `q=Bicicléta` o `q=bici`
- **THEN** se obtienen los anuncios con «bicicleta» o «Bicicletas» en el título o la descripción

#### Scenario: Sin resultados
- **WHEN** ninguna descripción contiene «patinete» y se busca `q=patinete`
- **THEN** la respuesta es `200` con `items: []` y `total: 0`

### Requirement: Longitud de la búsqueda
`q` vacío o solo con espacios SHALL equivaler a no enviarlo; con 1 carácter tras recortar MUST responder `422` con «La búsqueda debe tener al menos 2 caracteres.»; con más de 160, `422`.

#### Scenario: Demasiado corta
- **WHEN** se envía `q=a`
- **THEN** la respuesta es `422` en `query.q`

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

