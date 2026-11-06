## MODIFIED Requirements

### Requirement: Detalle de un anuncio
`/anuncios/<id>` SHALL mostrar el título, las fotografías (galería navegable con teclado cuya imagen principal abre el visor a pantalla completa), la descripción respetando los saltos de línea y sin interpretar HTML, la categoría, el tipo, el precio (o «Gratis»), «Reservado» si aplica, la fecha de publicación y el nombre del anunciante, con un enlace de vuelta a la comunidad.

#### Scenario: Desde el listado
- **WHEN** un miembro abre un anuncio desde el listado
- **THEN** ve toda su información y la del anunciante

## ADDED Requirements

### Requirement: Visor de imágenes a pantalla completa
Pulsar la imagen principal del detalle («Ampliar imagen N de M») SHALL abrir un diálogo modal con la imagen a pantalla completa sobre fondo oscuro, el contador «N / M» y «Cerrar». Con varias imágenes SHALL ofrecer «Imagen anterior» e «Imagen siguiente», las flechas del teclado y el deslizamiento horizontal, de forma circular. «Cerrar», Escape o el fondo MUST cerrarlo y devolver el foco, y el detalle SHALL mostrar la última imagen vista.

#### Scenario: Ampliar
- **WHEN** un miembro pulsa la imagen principal
- **THEN** la ve a pantalla completa con el contador y «Cerrar»

#### Scenario: Carrusel
- **WHEN** en la última imagen pulsa «Imagen siguiente» o desliza el dedo a la izquierda
- **THEN** ve la primera

#### Scenario: Una sola imagen
- **WHEN** el anuncio tiene una única fotografía
- **THEN** el visor no muestra las flechas

#### Scenario: Cerrar
- **WHEN** pulsa Escape tras pasar a la tercera imagen
- **THEN** vuelve al detalle con la tercera imagen como principal
