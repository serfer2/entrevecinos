## ADDED Requirements

### Requirement: Retirar y restaurar anuncios desde el detalle
Los gestores de la comunidad SHALL ver «Retirar anuncio» (con confirmación) en un anuncio visible y «Restaurar anuncio» en uno retirado; al retirar vuelven al listado con «Anuncio retirado.» y el anuncio deja de aparecer. El autor y los gestores ven en un anuncio retirado «Este anuncio está retirado y no se muestra en la comunidad.»; a un miembro sin rol MUST NOT ofrecérsele la retirada.

#### Scenario: Retirada
- **WHEN** un administrador pulsa «Retirar anuncio» y confirma
- **THEN** vuelve al listado con «Anuncio retirado.» y el anuncio ya no aparece

#### Scenario: Miembro sin rol
- **WHEN** un miembro sin rol abre el anuncio de otro vecino
- **THEN** no ve «Retirar anuncio»
