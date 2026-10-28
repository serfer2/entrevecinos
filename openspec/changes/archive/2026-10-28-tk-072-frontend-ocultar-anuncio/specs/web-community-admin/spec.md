## RENAMED Requirements

- FROM: `### Requirement: Retirar y restaurar anuncios desde el detalle`
- TO: `### Requirement: Ocultar y restaurar anuncios desde el detalle`

## MODIFIED Requirements

### Requirement: Ocultar y restaurar anuncios desde el detalle
Los gestores de la comunidad SHALL ver «Ocultar anuncio» (con confirmación) en un anuncio visible y «Restaurar anuncio» en uno oculto; al ocultar vuelven al listado con «Anuncio ocultado.» y el anuncio deja de aparecer. El autor y los gestores ven en un anuncio oculto «Este anuncio está oculto y no se muestra en la comunidad.»; a un miembro sin rol MUST NOT ofrecérsele la ocultación.

#### Scenario: Ocultación
- **WHEN** un administrador pulsa «Ocultar anuncio» y confirma
- **THEN** vuelve al listado con «Anuncio ocultado.» y el anuncio ya no aparece

#### Scenario: Miembro sin rol
- **WHEN** un miembro sin rol abre el anuncio de otro vecino
- **THEN** no ve «Ocultar anuncio»
