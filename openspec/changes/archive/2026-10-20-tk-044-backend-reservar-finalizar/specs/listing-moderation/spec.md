## ADDED Requirements

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
