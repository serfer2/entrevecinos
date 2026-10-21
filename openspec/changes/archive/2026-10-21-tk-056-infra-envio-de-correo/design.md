## Context

La API no enviaba correo. Mailpit recoge por SMTP todo lo que se envía y lo muestra en el navegador.

## Decisions

- **Mailpit con versión fija (`axllent/mailpit:v1.31.4`)**, sin volumen: los correos de desarrollo se pierden al recrear el contenedor.
- **Redes `data` y `edge`:** la API llega por `data`; `edge` solo para publicar la interfaz, ligada a `127.0.0.1`.
- **`Settings` exige `SMTP_HOST`, `MAIL_FROM` y `WEB_PUBLIC_URL`;** en producción además `SMTP_STARTTLS=true` y `WEB_PUBLIC_URL` en `https`.

## Risks / Trade-offs

- [Los `.env` existentes no tienen las variables nuevas y la API no arranca] → aviso en la documentación (TK-062).
