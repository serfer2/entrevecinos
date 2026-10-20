# listing-deletion Specification

## Purpose
Borrado lógico de anuncios por su autor o por la gestión de la comunidad.
## Requirements
### Requirement: Eliminar un anuncio
`DELETE /v1/listings/{listing_id}` SHALL marcar el anuncio con `deleted_at` y `status = deleted` y responder `204` cuando lo pide su autor, un `community_admin`/`moderator` aprobado de su comunidad o un `platform_admin`; a cualquier otro usuario MUST responder `403`.

#### Scenario: Autor
- **WHEN** el autor elimina su anuncio
- **THEN** recibe `204` y el anuncio queda con `deleted_at` y `status = deleted`

#### Scenario: Miembro sin rol
- **WHEN** un miembro que no es el autor intenta eliminarlo
- **THEN** recibe `403`

### Requirement: Un anuncio eliminado no aparece en ninguna lectura
Las lecturas de anuncios MUST excluir los eliminados: volver a eliminarlo SHALL responder `404` y sus imágenes dejan de ser legibles para los miembros (salvo para quien las subió).

#### Scenario: Borrar dos veces
- **WHEN** se envía `DELETE` sobre un anuncio ya eliminado
- **THEN** la respuesta es `404`

