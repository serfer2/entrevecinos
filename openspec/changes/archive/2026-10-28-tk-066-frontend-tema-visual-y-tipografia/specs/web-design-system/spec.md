## ADDED Requirements

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
