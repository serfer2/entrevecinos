# listing-detail Specification

## Purpose
Detalle de un anuncio y su regla de visibilidad (`ListingVisibility`).
## Requirements
### Requirement: Detalle de un anuncio
`GET /v1/listings/{listing_id}` SHALL devolver a los miembros aprobados de su comunidad el `Listing` completo (título, descripción, `category_id`, tipo, precio, imágenes ordenadas, `published_at`, `updated_at` y `owner` con nombre y teléfono).

#### Scenario: Miembro
- **WHEN** un miembro aprobado pide un anuncio activo de su comunidad
- **THEN** recibe `200` con el anuncio y su anunciante

### Requirement: Visibilidad del anuncio
Un anuncio inexistente, eliminado o de una cuenta eliminada MUST responder `404`; quien no es miembro aprobado de la comunidad `403` (con `status` si tiene membresía); un anuncio `hidden` SHALL verlo solo su autor y los gestores de la comunidad, y el resto MUST recibir `404`. Un anuncio `completed` sigue visible para los miembros.

#### Scenario: Retirado
- **WHEN** un miembro que no es autor ni gestor pide un anuncio `hidden`
- **THEN** recibe `404`

#### Scenario: Ajeno
- **WHEN** un usuario de otra comunidad pide el anuncio
- **THEN** recibe `403`

### Requirement: Datos de contacto del anunciante
`Listing.owner` SHALL incluir `email` y `phone` (`null` si el anunciante no lo informó), y solo MUST entregarse a miembros aprobados de la comunidad del anuncio: a cualquier otro usuario el detalle y el listado responden `401` o `403` sin el teléfono ni el correo.

#### Scenario: Miembro
- **WHEN** un miembro aprobado pide el detalle
- **THEN** `owner` incluye el correo y el teléfono del anunciante

#### Scenario: Sin teléfono
- **WHEN** el anunciante no tiene teléfono
- **THEN** `owner.phone` es `null` y `owner.email` está informado

#### Scenario: No miembro
- **WHEN** un usuario pendiente, rechazado, bloqueado o ajeno pide el detalle o el listado
- **THEN** recibe `403` y la respuesta no contiene el correo ni el teléfono

