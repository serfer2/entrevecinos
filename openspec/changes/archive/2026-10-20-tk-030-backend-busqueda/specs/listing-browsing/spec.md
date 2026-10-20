## ADDED Requirements

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
