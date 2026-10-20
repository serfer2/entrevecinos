## ADDED Requirements

### Requirement: Ordenar el listado
El listado SHALL ofrecer «Ordenar por» con «Más recientes» (por defecto), «Más antiguos», «Precio: de menor a mayor» y «Precio: de mayor a menor»; el orden elegido MUST conservarse al paginar, buscar, filtrar y cambiar de comunidad. Al ordenar por precio se muestra «Los anuncios sin precio aparecen al final.».

#### Scenario: Por precio
- **WHEN** el vecino elige «Precio: de menor a mayor»
- **THEN** los anuncios se ordenan por precio ascendente, los sin precio al final, y ve la nota

#### Scenario: Paginación
- **WHEN** pasa a la página siguiente
- **THEN** se mantiene el orden elegido
