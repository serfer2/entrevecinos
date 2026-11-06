## ADDED Requirements

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
