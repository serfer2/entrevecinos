## Context

El registro devolvía un JWT. La web es el único cliente.

## Decisions

- **Token `secrets.token_urlsafe(32)`, guardado como SHA-256;** crear uno borra los anteriores del usuario: solo vale el último enlace.
- **Envío tras responder con `BackgroundTasks`:** un fallo del SMTP no deshace el registro; se registra en el log y el usuario puede pedir otro correo (TK-059).
- **Validación por `POST` desde la web, no `GET` a la API:** los escáneres de enlaces no consumen el token por accidente sin pasar por la web, que trata el enlace repetido como validado (TK-060).
- **`403 email_not_verified` solo tras comprobar la contraseña:** no revela qué correos existen.
- **`410` incluye el correo** para ofrecer el reenvío sin pedirlo: quien tiene el token recibió el mensaje.

## Risks / Trade-offs

- [Cambio incompatible en `registerUser`] → solo lo usa la web, que se adapta en TK-060.
- [Tokens caducados sin limpieza periódica] → se borran al reenviar o al validar.
