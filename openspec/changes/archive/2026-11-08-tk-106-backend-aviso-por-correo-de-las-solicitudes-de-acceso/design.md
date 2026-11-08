## Context

`RequestMembership` crea la membresía y la devuelve; la usan el endpoint y varias pruebas. El correo de la autenticación se prepara en la aplicación (`OutgoingEmail`), reserva cupo con `EmailQuota` y se envía con `BackgroundTasks` (`send_in_background`), cuyo mensaje de error alimenta la alarma `email-send-failures`. TK-108 enviará otro aviso al aprobar una solicitud.

## Goals / Non-Goals

**Goals:** avisar a la administración de cada solicitud sin que el correo condicione la solicitud.

**Non-Goals:** aviso al solicitante (TK-108); texto de la web (TK-107); preferencias de avisos.

## Decisions

- **`MembershipNotices` aparte de `RequestMembership`:** prepara los avisos (destinatarios, cupo y plantilla) y lo reutilizará TK-108 para el de aprobación. `RequestMembership` no cambia su firma; el endpoint llama a los dos. El ticket proponía que `RequestMembership` devolviera los mensajes; separarlo evita tocar sus pruebas y concentra las plantillas de comunidades.
- **Destinatarios en el repositorio:** `list_admin_recipients(community_id) -> list[User]`, membresías `approved` con rol `community_admin`, usuario `is_active` y `deleted_at` nulo, ordenados por nombre. Solo `community_admin`: son quienes pueden aprobar.
- **Cupo:** una plaza por destinatario; si se agota a mitad, los ya reservados se envían y el resto no (`EmailQuotaExceeded` capturada, ya registrada por `EmailQuota`).
- **`send_in_background` en `presentation/v1/mail.py`:** lo usan la autenticación y las comunidades; conserva el mensaje «No se pudo enviar el correo «%s»» que vigila la alarma.
- **Orden en el endpoint:** solicitud creada → avisos preparados (misma transacción, por la reserva de cupo) → envío tras responder.

## Risks / Trade-offs

- [Pedir acceso a muchas comunidades genera un aviso por cada una] → una solicitud por comunidad (`409`), límite general del proxy y cupo mensual con aviso al 80 %.
