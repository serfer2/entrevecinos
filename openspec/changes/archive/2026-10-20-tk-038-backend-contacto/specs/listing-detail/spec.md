## ADDED Requirements

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
