## ADDED Requirements

### Requirement: Reservar y finalizar desde el detalle
El autor SHALL ver en su anuncio activo «Marcar como reservado» y «Marcar como finalizado», y en uno reservado «Quitar reserva» y «Marcar como finalizado»; finalizar MUST pedir confirmación. Tras cada cambio vuelve al detalle con el mensaje correspondiente; un anuncio finalizado muestra «Finalizado» y «Este anuncio está finalizado.», sin botones de estado ni «Editar». Ningún otro usuario ve estas opciones.

#### Scenario: Reservar
- **WHEN** el autor pulsa «Marcar como reservado»
- **THEN** ve «Anuncio marcado como reservado.» y la etiqueta «Reservado» en el detalle y en el listado

#### Scenario: Finalizar
- **WHEN** el autor pulsa «Marcar como finalizado» y confirma
- **THEN** ve el aviso de finalizado, sin botones de estado ni «Editar», y el anuncio deja de aparecer en el listado
