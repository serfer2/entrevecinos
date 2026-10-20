## ADDED Requirements

### Requirement: Listado de anuncios en la comunidad
La página de una comunidad SHALL mostrar a los miembros aprobados sus anuncios en tarjetas (portada, título, tipo, precio o «Gratis», «Reservado» si aplica y fecha), del más reciente al más antiguo, paginados de 24 en 24; a quien no es miembro aprobado MUST mostrarle solo el aviso de acceso, sin pedir el listado.

#### Scenario: Con anuncios
- **WHEN** un miembro aprobado abre la comunidad
- **THEN** ve las tarjetas de los anuncios, los más recientes primero

#### Scenario: Sin anuncios
- **WHEN** la comunidad no tiene anuncios
- **THEN** ve «Todavía no hay anuncios en esta comunidad.» y «Publica el primero»
