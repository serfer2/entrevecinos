## ADDED Requirements

### Requirement: Categorías activas
`GET /v1/categories` SHALL devolver `{items: Category[]}` con las categorías activas ordenadas por nombre y «Otros» al final.

#### Scenario: Listado
- **WHEN** un usuario autenticado pide las categorías
- **THEN** recibe las activas, con «Otros» en último lugar

### Requirement: Publicar un anuncio
`POST /v1/communities/{community_id}/listings` SHALL crear, para un miembro aprobado, un anuncio `active` con `published_at` actual y responder `201` con `Listing` (`owner` con nombre y teléfono del autor, `images` ordenadas con la primera como portada).

#### Scenario: Con imágenes
- **WHEN** un miembro publica con tres imágenes suyas
- **THEN** `images` tiene tres elementos en ese orden y el primero tiene `is_cover: true`

### Requirement: Precio opcional
Sin precio, `price` y `currency` SHALL ser `null`; con precio sin moneda, `currency` SHALL ser `EUR`; una moneda sin precio MUST responder `422`.

#### Scenario: Precio sin moneda
- **WHEN** se publica con `price: 45`
- **THEN** la respuesta tiene `currency: "EUR"`

### Requirement: Validación del anuncio
Faltar título, descripción, categoría o tipo, superar sus límites (160 y 5000 caracteres) o enviar más de 10 imágenes MUST responder `422` con un error por campo; una categoría inexistente o inactiva `422` en `category_id`; una imagen ajena o ya usada `400`. En ningún caso se crea el anuncio.

#### Scenario: Imagen ajena
- **WHEN** se publica con una imagen subida por otro usuario
- **THEN** la respuesta es `400 {"detail": "Alguna imagen no es válida."}`

### Requirement: Solo miembros aprobados
Un usuario sin membresía aprobada MUST recibir `403` (con `status` si tiene membresía) y no se crea el anuncio.

#### Scenario: Pendiente
- **WHEN** un usuario con la solicitud pendiente intenta publicar
- **THEN** recibe `403` con `status: "pending"`
