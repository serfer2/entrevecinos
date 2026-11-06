## MODIFIED Requirements

### Requirement: Solo miembros aprobados
El botón «Publicar anuncio» SHALL mostrarse solo a miembros aprobados y a `platform_admin`, y `/anuncios/nuevo` MUST mostrar el aviso de acceso a quien no lo es.

#### Scenario: Pendiente
- **WHEN** un vecino con la solicitud pendiente abre `/anuncios/nuevo`
- **THEN** ve el aviso de solicitud pendiente y ningún formulario

#### Scenario: Administrador de plataforma
- **WHEN** un `platform_admin` sin membresía aprobada abre `/anuncios/nuevo`
- **THEN** ve el formulario

### Requirement: Listado de anuncios en la comunidad
La página de una comunidad SHALL mostrar a los miembros aprobados y a `platform_admin` sus anuncios en tarjetas (portada, título, tipo, precio o «Gratis», «Reservado» si aplica y fecha), del más reciente al más antiguo, paginados de 24 en 24; a quien no tiene acceso MUST mostrarle solo el aviso de acceso, sin pedir el listado.

#### Scenario: Con anuncios
- **WHEN** un miembro aprobado abre la comunidad
- **THEN** ve las tarjetas de los anuncios, los más recientes primero

#### Scenario: Sin anuncios
- **WHEN** la comunidad no tiene anuncios
- **THEN** ve «Todavía no hay anuncios en esta comunidad.» y «Publica el primero»
