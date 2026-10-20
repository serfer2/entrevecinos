# web-listings Specification

## Purpose
Pantallas de anuncios: publicar, listar, buscar, detalle, editar y estados.
## Requirements
### Requirement: Publicar un anuncio desde la interfaz
`/comunidades/<id>/anuncios/nuevo` SHALL mostrar a los miembros aprobados un formulario con título, descripción, categoría, tipo (Vendo, Busco, Ofrezco, Necesito, Regalo, Otros), precio opcional en euros y hasta 10 fotografías; al publicar, el vecino vuelve a la comunidad con «Anuncio publicado.».

#### Scenario: Publicación correcta
- **WHEN** un miembro completa los campos obligatorios y publica
- **THEN** vuelve a `/comunidades/<id>` con «Anuncio publicado.»

### Requirement: Fotografías
El formulario SHALL subir cada fotografía al elegirla, mostrar su miniatura a través de `/media/<id>`, permitir quitarla y cambiar su orden (la primera es la portada) y MUST rechazar en el propio fichero los de más de 5 MB o de otro formato.

#### Scenario: Reordenar
- **WHEN** el vecino sube tres fotos, mueve la tercera arriba y publica
- **THEN** el anuncio se crea con ese orden y la tercera como portada

### Requirement: Validación
Sin título, descripción, categoría o tipo, o con un precio no válido, el formulario MUST mostrar el error junto al campo sin llamar a la API, conservando lo escrito y las fotos.

#### Scenario: Sin título
- **WHEN** se publica sin título
- **THEN** se ve «El título es obligatorio.» y no se publica nada

### Requirement: Lectura de imágenes sin exponer el token
`GET /media/<id>` SHALL redirigir a la URL prefirmada que devuelve la API usando el token de la *cookie*, y MUST responder `404` cuando la API responde `403` o `404`.

#### Scenario: Imagen ajena
- **WHEN** la API responde `403`
- **THEN** la ruta responde `404`

### Requirement: Solo miembros aprobados
El botón «Publicar anuncio» SHALL mostrarse solo a miembros aprobados, y `/anuncios/nuevo` MUST mostrar el aviso de acceso a quien no lo es.

#### Scenario: Pendiente
- **WHEN** un vecino con la solicitud pendiente abre `/anuncios/nuevo`
- **THEN** ve el aviso de solicitud pendiente y ningún formulario

### Requirement: Listado de anuncios en la comunidad
La página de una comunidad SHALL mostrar a los miembros aprobados sus anuncios en tarjetas (portada, título, tipo, precio o «Gratis», «Reservado» si aplica y fecha), del más reciente al más antiguo, paginados de 24 en 24; a quien no es miembro aprobado MUST mostrarle solo el aviso de acceso, sin pedir el listado.

#### Scenario: Con anuncios
- **WHEN** un miembro aprobado abre la comunidad
- **THEN** ve las tarjetas de los anuncios, los más recientes primero

#### Scenario: Sin anuncios
- **WHEN** la comunidad no tiene anuncios
- **THEN** ve «Todavía no hay anuncios en esta comunidad.» y «Publica el primero»

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

