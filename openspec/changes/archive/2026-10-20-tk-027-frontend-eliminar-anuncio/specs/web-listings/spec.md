## ADDED Requirements

### Requirement: Eliminar un anuncio propio desde la interfaz
El autor SHALL ver «Eliminar anuncio» en el detalle; al pulsarlo se MUST pedir confirmación («¿Eliminar este anuncio?»), y al confirmar vuelve a la comunidad con «Anuncio eliminado.» y el anuncio ya no aparece. Si cancela, no pasa nada.

#### Scenario: Confirmar
- **WHEN** el autor pulsa «Eliminar anuncio» y después «Eliminar»
- **THEN** vuelve a la comunidad con «Anuncio eliminado.» y el anuncio no aparece en el listado

#### Scenario: Otro vecino
- **WHEN** otro miembro abre el detalle
- **THEN** no ve la opción de eliminarlo
