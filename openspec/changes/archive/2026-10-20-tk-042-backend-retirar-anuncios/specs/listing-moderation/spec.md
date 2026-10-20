## ADDED Requirements

### Requirement: Retirar y restaurar anuncios
`PATCH /v1/listings/{listing_id}/status` SHALL permitir a `community_admin`, `moderator` o `platform_admin` retirar un anuncio visible (`hidden`, registrando `hidden_by` y `hidden_at`) y restaurarlo (`active`, vaciando ambos). Un anuncio retirado MUST desaparecer del listado y de las búsquedas, y su detalle responder `404` a quien no es autor ni gestor. Cualquier otro usuario, incluido el autor, MUST recibir `403`; una transición no permitida `409`; un anuncio eliminado `404`.

#### Scenario: Retirada
- **WHEN** un administrador envía `{"status": "hidden"}`
- **THEN** recibe `200` y el anuncio deja de aparecer en el listado y en las búsquedas

#### Scenario: Miembro sin rol
- **WHEN** un miembro sin rol intenta retirar el anuncio de otro vecino
- **THEN** recibe `403`

#### Scenario: Restaurar
- **WHEN** el administrador envía `{"status": "active"}` sobre un anuncio retirado
- **THEN** vuelve a aparecer en el listado
