# web-design-system Specification

## Purpose
Identidad visual y estructura común de las páginas web: paleta, tipografía, logotipo, componentes y adaptación a móvil.
## Requirements
### Requirement: Identidad visual
La web SHALL usar una paleta inspirada en la naturaleza definida una sola vez en `globals.css` (`emerald` verde musgo para acciones, enlaces y precio; `gray` neutros cálidos con `gray-50` como fondo de página; `amber` ocre para avisos y «Reservado»; `red` terracota para errores y acciones destructivas), Figtree como fuente de texto y Fraunces en `h1` y `h2`, autoalojadas con `next/font`. El texto MUST mantener contraste AA.

#### Scenario: Cualquier página
- **WHEN** el vecino abre cualquier página
- **THEN** ve la paleta, la tipografía y el logotipo de EntreVecinos

#### Scenario: CSP
- **WHEN** se cargan las fuentes
- **THEN** se sirven desde el propio dominio sin cambiar `font-src 'self'`

### Requirement: Foco visible
Los enlaces, botones y campos SHALL mostrar un contorno verde al recibir el foco con el teclado.

#### Scenario: Navegación con teclado
- **WHEN** el vecino recorre la página con Tab
- **THEN** el elemento enfocado muestra el contorno

### Requirement: Logotipo
El logotipo (`BrandMark`) SHALL combinar un icono decorativo (`aria-hidden`) con el nombre «EntreVecinos» como texto.

#### Scenario: Lector de pantalla
- **WHEN** un lector de pantalla llega al logotipo
- **THEN** anuncia solo «EntreVecinos»

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

### Requirement: Campos ajustados a su columna
Los campos de texto, selección y área de texto SHALL ocupar el ancho de su columna sin desbordarla en ningún navegador soportado.

#### Scenario: Buscador de comunidades en Firefox
- **WHEN** un vecino abre `/comunidades` en Firefox de escritorio
- **THEN** los tres campos y «Buscar» caben dentro del panel

### Requirement: Campo de precio
El precio del formulario de anuncio SHALL medir como mucho 20 rem y mostrar «€» dentro del campo, alineado con el importe y oculto a los lectores de pantalla.

#### Scenario: Publicar en Firefox
- **WHEN** un miembro publica o edita un anuncio en Firefox
- **THEN** el precio tiene un ancho proporcionado y el «€» aparece junto al importe
