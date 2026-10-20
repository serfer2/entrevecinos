## ADDED Requirements

### Requirement: Buscador de anuncios
El listado de la comunidad SHALL incluir un buscador (formulario GET con `q`) que muestra solo los anuncios que coinciden y «N resultados para "…"»; sin resultados MUST mostrar «No hay anuncios que coincidan con "…".» y «Ver todos los anuncios»; «Limpiar» vuelve al listado completo. La paginación conserva la búsqueda.

#### Scenario: Coincidencias
- **WHEN** un miembro busca «bici»
- **THEN** ve solo los anuncios que la contienen y el número de resultados

#### Scenario: Limpiar
- **WHEN** pulsa «Limpiar»
- **THEN** vuelve a ver todos los anuncios de la comunidad

### Requirement: Búsqueda demasiado corta
Con un texto de menos de 2 caracteres, la página MUST mostrar «La búsqueda debe tener al menos 2 caracteres.» y el listado sin filtrar, sin enviar esa búsqueda a la API.

#### Scenario: Un carácter
- **WHEN** se busca «a»
- **THEN** se ve el aviso y el listado no cambia
