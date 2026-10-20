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

### Requirement: Editar un anuncio propio desde la interfaz
El autor SHALL ver «Editar anuncio» en el detalle y, en `/anuncios/<id>/editar`, el formulario precargado; al guardar vuelve al detalle con «Anuncio actualizado.». Solo se envían los campos cambiados y las imágenes si cambió su orden o portada.

#### Scenario: Edición correcta
- **WHEN** el autor cambia título, precio y el orden de las fotos y guarda
- **THEN** vuelve al detalle con «Anuncio actualizado.» y la información nueva

### Requirement: Validación al editar
Con el título o la descripción vacíos, el formulario MUST mostrar el error en el campo sin modificar el anuncio.

#### Scenario: Título vacío
- **WHEN** el autor vacía el título y guarda
- **THEN** ve «El título es obligatorio.» y el detalle conserva el título anterior

### Requirement: Solo el autor edita
A quien no es el autor no se le SHALL ofrecer «Editar anuncio», y `/anuncios/<id>/editar` MUST mostrarle «Solo quien publicó el anuncio puede editarlo.».

#### Scenario: Otro vecino
- **WHEN** otro miembro abre la URL de edición
- **THEN** ve el aviso y ningún formulario

### Requirement: Eliminar un anuncio propio desde la interfaz
El autor SHALL ver «Eliminar anuncio» en el detalle; al pulsarlo se MUST pedir confirmación («¿Eliminar este anuncio?»), y al confirmar vuelve a la comunidad con «Anuncio eliminado.» y el anuncio ya no aparece. Si cancela, no pasa nada.

#### Scenario: Confirmar
- **WHEN** el autor pulsa «Eliminar anuncio» y después «Eliminar»
- **THEN** vuelve a la comunidad con «Anuncio eliminado.» y el anuncio no aparece en el listado

#### Scenario: Otro vecino
- **WHEN** otro miembro abre el detalle
- **THEN** no ve la opción de eliminarlo

### Requirement: Buscador de anuncios
El listado de la comunidad SHALL incluir un buscador (formulario GET con `q`) que muestra solo los anuncios que coinciden y «N resultados para "…"»; sin resultados MUST mostrar «No hay anuncios que coincidan con "…".» y «Ver todos los anuncios»; «Limpiar» vuelve al listado completo. La paginación conserva la búsqueda.

#### Scenario: Coincidencias
- **WHEN** un miembro busca «bici»
- **THEN** ve solo los anuncios que la contienen y el número de resultados

#### Scenario: Limpiar
- **WHEN** pulsa «Limpiar»
- **THEN** vuelve a ver todos los anuncios de la comunidad

### Requirement: Búsqueda demasiado corta
Con un texto de menos de 2 caracteres, la página MUST mostrar «La búsqueda debe tener al menos 2 caracteres.» y el listado sin filtrar, sin enviar esa búsqueda a la API.

#### Scenario: Un carácter
- **WHEN** se busca «a»
- **THEN** se ve el aviso y el listado no cambia

### Requirement: Filtros del listado
El listado SHALL ofrecer los filtros «Tipo» (Vendo, Busco, Ofrezco, Necesito, Regalo, Otros) y «Categoría» en el mismo formulario GET que la búsqueda, combinables entre sí y con la palabra clave; la URL MUST reflejarlos. Sin resultados con filtros se muestra «No hay anuncios con estos filtros.» y «Limpiar filtros».

#### Scenario: Por tipo
- **WHEN** un miembro selecciona «Vendo»
- **THEN** ve solo anuncios de tipo «Vendo»

#### Scenario: Combinados
- **WHEN** ha escrito una palabra clave y además selecciona un tipo
- **THEN** ve solo los anuncios que cumplen ambas condiciones y la URL lleva los dos parámetros

### Requirement: Cambio de comunidad
Si el vecino es miembro aprobado de dos o más comunidades, el listado SHALL mostrar un selector «Comunidad» que lleva a la elegida conservando la búsqueda y los filtros.

#### Scenario: Otra comunidad
- **WHEN** elige otra comunidad en el selector
- **THEN** ve únicamente sus anuncios, con los mismos filtros aplicados

