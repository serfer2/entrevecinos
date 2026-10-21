## ADDED Requirements

### Requirement: Configuración del correo
La API MUST negarse a arrancar sin `SMTP_HOST`, `MAIL_FROM` o `WEB_PUBLIC_URL`. `SMTP_PORT` (por defecto 587), `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_STARTTLS` (por defecto `true`) y `EMAIL_VERIFICATION_TTL_HOURS` (`> 0`, por defecto 24) son opcionales. En producción, `SMTP_STARTTLS` MUST ser `true` y `WEB_PUBLIC_URL` MUST usar `https`.

#### Scenario: Falta WEB_PUBLIC_URL
- **WHEN** se crea la configuración sin `WEB_PUBLIC_URL`
- **THEN** se lanza un error de validación que nombra `web_public_url`

#### Scenario: Producción sin STARTTLS
- **WHEN** `ENVIRONMENT=production` y `SMTP_STARTTLS=false`
- **THEN** la configuración falla al cargarse

### Requirement: Buzón de desarrollo
El entorno de desarrollo SHALL incluir el servicio `mail` (Mailpit), accesible desde la API en `mail:1025` y con su interfaz web publicada solo en `127.0.0.1:${MAIL_UI_HOST_PORT:-8025}`.

#### Scenario: Correo de prueba
- **WHEN** el contenedor `api` envía un correo a `mail:1025`
- **THEN** aparece en `http://localhost:8025`
