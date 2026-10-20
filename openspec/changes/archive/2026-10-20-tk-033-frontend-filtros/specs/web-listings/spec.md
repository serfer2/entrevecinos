## ADDED Requirements

### Requirement: Filtros del listado
El listado SHALL ofrecer los filtros «Tipo» (Vendo, Busco, Ofrezco, Necesito, Regalo, Otros) y «Categoría» en el mismo formulario GET que la búsqueda, combinables entre sí y con la palabra clave; la URL MUST reflejarlos. Sin resultados con filtros se muestra «No hay anuncios con estos filtros.» y «Limpiar filtros».

#### Scenario: Por tipo
- **WHEN** un miembro selecciona «Vendo»
- **THEN** ve solo anuncios de tipo «Vendo»

#### Scenario: Combinados
- **WHEN** ha escrito una palabra clave y además selecciona un tipo
- **THEN** ve solo los anuncios que cumplen ambas condiciones y la URL lleva los dos parámetros

### Requirement: Cambio de comunidad
Si el vecino es miembro aprobado de dos o más comunidades, el listado SHALL mostrar un selector «Comunidad» que lleva a la elegida conservando la búsqueda y los filtros.

#### Scenario: Otra comunidad
- **WHEN** elige otra comunidad en el selector
- **THEN** ve únicamente sus anuncios, con los mismos filtros aplicados
