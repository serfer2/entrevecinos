## Context

`AccessNotice` muestra en la página de la comunidad un aviso según el estado de la membresía; no tiene pruebas propias. El formulario de anuncios tiene otro aviso de solicitud pendiente («Podrás publicar cuando un administrador la apruebe.»).

## Goals / Non-Goals

**Goals:** informar al solicitante de que su solicitud llegó a la administración y de que recibirá un correo al aprobarse.

**Non-Goals:** el aviso del formulario de anuncios, que se ve al intentar publicar y no cambia de sentido.

## Decisions

- **«Hemos enviado tu solicitud a la administración»** es cierto aunque no salga el correo a la administración: la solicitud aparece en su lista de pendientes.
- **«Te avisaremos por correo cuando la apruebe»**: es lo que hace TK-108. Si un día no saliera por falta de cupo, la comunidad aparece igualmente en «Mis comunidades».

## Risks / Trade-offs

- [El correo de aprobación podría no llegar (cupo agotado o fallo del proveedor)] → caso raro y vigilado por alarmas; el acceso no depende del correo.
