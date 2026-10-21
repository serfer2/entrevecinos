## Why

La Épica 10 cambia el registro (ya no inicia la sesión), añade un servicio de correo, variables de entorno, una tabla y endpoints, y la documentación general no lo reflejaba. Ticket: `docs/product/tickets/00-infra/TK-062-docs-validacion-del-correo.md`.

## What Changes

- `readme.md`: MVP, diagramas de arquitectura y despliegue con SMTP/Mailpit, componentes, modelo de datos (`users.email_verified_at`, `ck_users_active_requires_verified_email`, `email_verification`) y nota de instalación con las variables nuevas.
- `docs/product/user-stories.md`: HU-01 AC1/AC2 y HU-02 AC1/AC4 coherentes con HU-25 y HU-26.
- `infra/README.md`: servicio `mail`, variables y aviso para los `.env` existentes.
- `apps/api/README.md`: configuración, endpoints de validación, `EmailSender`/`SmtpEmailSender` y `FakeEmailSender`.
- `apps/web/README.md`: rutas públicas y flujo de registro y validación.

## Capabilities

### New Capabilities

### Modified Capabilities

Ninguna: solo documentación; las especificaciones se actualizaron con TK-056 a TK-061.

## Impact

- Solo documentación.
