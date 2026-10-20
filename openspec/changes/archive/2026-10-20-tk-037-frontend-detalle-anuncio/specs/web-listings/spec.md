## ADDED Requirements

### Requirement: Detalle de un anuncio
`/anuncios/<id>` SHALL mostrar el título, las fotografías (galería navegable con teclado), la descripción respetando los saltos de línea y sin interpretar HTML, la categoría, el tipo, el precio (o «Gratis»), «Reservado» si aplica, la fecha de publicación y el nombre del anunciante, con un enlace de vuelta a la comunidad.

#### Scenario: Desde el listado
- **WHEN** un miembro abre un anuncio desde el listado
- **THEN** ve toda su información y la del anunciante

### Requirement: Anuncio no disponible o sin acceso
Si la API responde `404`, la página SHALL mostrar «Este anuncio no está disponible. Puede que se haya eliminado o retirado.»; si responde `403`, «No tienes acceso a los anuncios de esta comunidad.».

#### Scenario: Eliminado
- **WHEN** se abre el enlace de un anuncio eliminado
- **THEN** se ve el mensaje de anuncio no disponible
