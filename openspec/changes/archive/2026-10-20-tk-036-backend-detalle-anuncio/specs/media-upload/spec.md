## MODIFIED Requirements

### Requirement: Leer una imagen
`GET /v1/media/{asset_id}` SHALL responder `302` a una URL prefirmada del host público (válida 300 s) a quien la subió o a quien puede ver (según `ListingVisibility`) el anuncio no eliminado que la usa; a cualquier otro usuario MUST responder `403`, y `404` si no existe.

#### Scenario: Miembro de la comunidad
- **WHEN** un miembro aprobado pide una imagen de un anuncio de su comunidad
- **THEN** recibe `302` con `Location` en `http://localhost:9000/…`

#### Scenario: Ajeno
- **WHEN** un usuario de otra comunidad la pide
- **THEN** recibe `403`
