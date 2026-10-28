## ADDED Requirements

### Requirement: Páginas públicas
El inicio de sesión, el registro y el error de validación del correo SHALL compartir un marco común (`AuthShell`) con el logotipo y el formulario sobre una superficie blanca.

#### Scenario: Inicio de sesión
- **WHEN** un visitante abre `/iniciar-sesion`
- **THEN** ve el logotipo y el formulario en el marco común

### Requirement: Tarjetas de anuncio
Cada tarjeta del listado SHALL destacar la fotografía, el título y el precio, con el tipo y, si aplica, «Reservado» (en ocre) sobre la imagen. Las animaciones MUST desactivarse con `prefers-reduced-motion`.

#### Scenario: Listado
- **WHEN** un miembro recorre el listado de su comunidad
- **THEN** cada tarjeta muestra imagen, tipo, título y precio destacado

### Requirement: Panel de búsqueda
La búsqueda, los filtros de tipo y categoría y el orden del listado SHALL agruparse en un mismo panel con un icono de lupa en el campo de búsqueda.

#### Scenario: Buscar y filtrar
- **WHEN** un miembro busca o filtra
- **THEN** todos los controles están en el mismo panel

### Requirement: Adaptación a móvil
Con un ancho de 390 px, el listado y el detalle MUST NOT tener desplazamiento horizontal y la cabecera MUST NOT quedar fija; la rejilla del listado SHALL pasar de 1 columna en móvil a 4 en pantallas grandes.

#### Scenario: Móvil
- **WHEN** un vecino abre el listado en un móvil de 390 px
- **THEN** ve una columna de tarjetas sin desplazamiento horizontal
