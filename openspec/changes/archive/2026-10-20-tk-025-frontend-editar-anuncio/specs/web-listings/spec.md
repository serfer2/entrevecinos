## ADDED Requirements

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
