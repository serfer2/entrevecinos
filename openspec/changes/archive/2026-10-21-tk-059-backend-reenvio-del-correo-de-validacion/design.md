## Context

TK-058 deja la cuenta pendiente hasta validar el correo; el usuario necesita poder pedir otro enlace.

## Decisions

- **Siempre `202` con el mismo cuerpo:** el reenvío no revela qué correos existen (HU-26 AC3).
- **Límite por cuenta de 60 segundos** con la fecha del último enlace (`created_at`); sin límite por IP.
- **El segundo registro no cambia la cuenta pendiente:** sus datos se descartan.
- **Envío tras responder con `BackgroundTasks`,** como en el registro.

## Risks / Trade-offs

- [El `409` del registro revela si un correo existe] → ya ocurría antes de la épica; el reenvío no añade información.
- [Una cuenta que nunca se valida ocupa su correo para siempre] → limpieza de pendientes antiguas en otra historia.
