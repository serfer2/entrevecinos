## MODIFIED Requirements

### Requirement: Configuración del correo
La API MUST negarse a arrancar sin `MAIL_FROM` o `WEB_PUBLIC_URL`. `MAIL_BACKEND` SHALL admitir `smtp` (por defecto) o `ses`, y MUST rechazar cualquier otro valor con un error en español que nombre la variable. Con `MAIL_BACKEND=smtp`, `SMTP_HOST` MUST estar definido. `SMTP_PORT` (por defecto 587), `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_STARTTLS` (por defecto `true`), `SES_REGION` (por defecto `eu-north-1`), `SES_CONFIGURATION_SET` y `EMAIL_VERIFICATION_TTL_HOURS` (`> 0`, por defecto 24) son opcionales. En producción, con `smtp`, `SMTP_STARTTLS` MUST ser `true`, y `WEB_PUBLIC_URL` MUST usar `https` con cualquier *backend*.

#### Scenario: Falta WEB_PUBLIC_URL
- **WHEN** se crea la configuración sin `WEB_PUBLIC_URL`
- **THEN** se lanza un error de validación que nombra `web_public_url`

#### Scenario: Producción sin STARTTLS
- **WHEN** `ENVIRONMENT=production`, `MAIL_BACKEND=smtp` y `SMTP_STARTTLS=false`
- **THEN** la configuración falla al cargarse

#### Scenario: SES sin SMTP
- **WHEN** `ENVIRONMENT=production`, `MAIL_BACKEND=ses`, sin `SMTP_HOST` y con `WEB_PUBLIC_URL` en `https`
- **THEN** la configuración se carga

#### Scenario: Backend desconocido
- **WHEN** `MAIL_BACKEND=sendgrid`
- **THEN** la configuración falla con «MAIL_BACKEND debe ser «smtp» o «ses».»

## ADDED Requirements

### Requirement: Envío por la API de SES
Con `MAIL_BACKEND=ses`, la API SHALL enviar cada correo con `SendEmail` de SES v2 desde `MAIL_FROM`, con el texto y el HTML en UTF-8 y, si está definido, con `SES_CONFIGURATION_SET`, usando las credenciales de la cadena por defecto de AWS; los errores de SES MUST tratarse como los de SMTP (se registran sin interrumpir el registro ni el reenvío).

#### Scenario: Correo de validación por SES
- **WHEN** un vecino se registra con `MAIL_BACKEND=ses` y `SES_CONFIGURATION_SET=entrevecinos-prod`
- **THEN** la API llama a `SendEmail` con el remitente, el destinatario, el asunto, el texto, el HTML y el *configuration set*

#### Scenario: SES rechaza el correo
- **WHEN** SES responde `MessageRejected`
- **THEN** el adaptador propaga el error y el flujo lo registra como un fallo de envío
