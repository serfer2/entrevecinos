# listing-moderation Specification

## Purpose
Retirada y restauración de anuncios por la gestión de la comunidad.
## Requirements
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

### Requirement: Reservar y finalizar un anuncio propio
`PATCH /v1/listings/{listing_id}/status` SHALL permitir al autor, con membresía aprobada, pasar su anuncio de `active` a `reserved` y viceversa, y de `active` o `reserved` a `completed`, sin cambiar `published_at`. `completed` es final: cambiar de nuevo su estado MUST responder `409` y editarlo `403`. Reservar o finalizar el anuncio de otro usuario, aunque sea gestor, MUST responder `403`.

#### Scenario: Reservar
- **WHEN** el autor envía `{"status": "reserved"}` sobre un anuncio activo
- **THEN** recibe `200` con `status: "reserved"` y el anuncio sigue en el listado

#### Scenario: Finalizar
- **WHEN** el autor envía `{"status": "completed"}`
- **THEN** recibe `200`, el anuncio deja de aparecer en el listado y en las búsquedas, y cualquier cambio de estado o edición posterior se rechaza

#### Scenario: Otro vecino
- **WHEN** un moderador intenta reservar el anuncio de otro
- **THEN** recibe `403`

