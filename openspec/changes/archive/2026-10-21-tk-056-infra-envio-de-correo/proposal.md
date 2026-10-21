## Why

HU-25: la validación del correo necesita enviar emails y el proyecto no tenía servicio de correo; en desarrollo no deben salir correos reales. Ticket: `docs/product/tickets/EP-10-validacion-del-correo-electronico/HU-25-validar-mi-correo-electronico-al-registrarme/TK-056-infra-envio-de-correo.md`.

## What Changes

- Servicio `mail` (Mailpit) en Compose: SMTP en `mail:1025` y la interfaz web en `127.0.0.1:${MAIL_UI_HOST_PORT:-8025}`.
- Variables `SMTP_*`, `MAIL_FROM`, `WEB_PUBLIC_URL`, `EMAIL_VERIFICATION_TTL_HOURS` y `MAIL_UI_HOST_PORT` en `.env.example`, `.env` local y `Settings`.
- `make dev` levanta `mail` y muestra su URL.

## Capabilities

### New Capabilities
- `email-delivery`: configuración del envío de correo por SMTP.

### Modified Capabilities
- `dev-automation`: `make dev` levanta también `mail`.

## Impact

- `infra/docker-compose.yml`, `.env.example`, `Makefile`, `apps/api` (`Settings`).
