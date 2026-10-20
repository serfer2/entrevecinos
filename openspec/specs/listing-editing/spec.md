# listing-editing Specification

## Purpose
Edición de anuncios propios: campos y conjunto de imágenes.
## Requirements
### Requirement: Editar un anuncio propio
`PATCH /v1/listings/{listing_id}` SHALL actualizar solo los campos enviados (`category_id`, `title`, `description`, `type`, `price`, `currency`) de un anuncio del autor y responder `200` con el `Listing` actualizado, sin cambiar `published_at`.

#### Scenario: Cambio parcial
- **WHEN** el autor envía `{"title": "Bicicleta infantil 16\"", "price": 40}`
- **THEN** recibe `200` con el título y el precio nuevos y el resto sin cambios

### Requirement: Validación de la edición
Un título o descripción en blanco o `null`, una categoría inactiva, una moneda sin precio resultante o un cuerpo vacío MUST responder `422` sin modificar el anuncio; `{"price": null}` SHALL borrar también la moneda.

#### Scenario: Título en blanco
- **WHEN** el autor envía `{"title": "  "}`
- **THEN** recibe `422` en `title` y el anuncio no cambia

### Requirement: Sustituir las imágenes
`PUT /v1/listings/{listing_id}/images` SHALL sustituir el conjunto de imágenes (0–10, en el orden enviado; portada la marcada o la primera). Las imágenes MUST ser del autor y estar libres o ya en este anuncio (si no, `400`); más de una portada o más de 10 imágenes → `422`.

#### Scenario: Cambiar la portada
- **WHEN** el autor envía las imágenes con otra marcada como portada
- **THEN** la respuesta tiene ese orden y esa portada

### Requirement: Solo el autor
Solo el autor, con membresía aprobada, SHALL poder editar; cualquier otro usuario (incluidos los administradores) MUST recibir `403`; un anuncio retirado (`hidden`) MUST responder `403` también al autor, y uno eliminado `404`.

#### Scenario: Administrador
- **WHEN** un administrador de la comunidad intenta editar el anuncio de otro
- **THEN** recibe `403` y no se modifica nada

