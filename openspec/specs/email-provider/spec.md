# email-provider Specification

## Purpose
Proveedor de correo de producción (Brevo por SMTP, con SES como vuelta atrás) y custodia de sus credenciales.
## Requirements
### Requirement: Proveedor de correo de producción
El correo de producción SHALL enviarse por SMTP con Brevo, con el dominio autenticado con el prefijo de marca `send`, y SES MUST seguir configurado como vuelta atrás. La decisión, su comparación por coste e integración, el estado real de SES y cómo volver MUST estar en `infra/aws/README.md`.

#### Scenario: Decisión documentada
- **WHEN** consulto «Decisiones de arquitectura» de `infra/aws/README.md`
- **THEN** encuentro por qué Brevo y no SES, el coste, los riesgos y cómo volver a SES

### Requirement: Credenciales SMTP fuera del repositorio
El usuario y la clave SMTP de Brevo SHALL guardarse solo en Parameter Store como `SecureString` (`/entrevecinos/prod/smtp/username` y `/entrevecinos/prod/smtp/password`) y MUST NOT aparecer en el repositorio, el estado de Terraform ni ficheros.

#### Scenario: Parámetros
- **WHEN** describo los parámetros de `/entrevecinos/prod/smtp/`
- **THEN** hay dos, de tipo `SecureString`

### Requirement: Dominio autenticado en Brevo
Route 53 SHALL publicar, gestionados por Terraform, el TXT de verificación `brevo-code` en el mismo conjunto que el SPF de la raíz, los dos CNAME de DKIM de Brevo y los CNAME de marca con el prefijo `send`, y el DMARC MUST conservar `adkim=s` y `aspf=r` al añadir el `rua` de Brevo. Ningún registro de Brevo MUST usar el nombre `mail`, reservado al MAIL FROM de SES.

#### Scenario: Registros publicados
- **WHEN** consulto el TXT de `entrevecinos.org` y `brevo1._domainkey.entrevecinos.org`
- **THEN** el TXT contiene `v=spf1 -all` y el `brevo-code`, y el CNAME apunta a `b1.entrevecinos-org.dkim.brevo.com`

### Requirement: Envío por Brevo desde una IP fija
La API de producción SHALL enviar por `smtp-relay.brevo.com:587` con STARTTLS y las credenciales de `/entrevecinos/prod/smtp/`, que `deploy.sh` MUST pasar solo por entorno. La instancia MUST tener una IP elástica, autorizada en Brevo, y su grupo de seguridad MUST permitir la salida TCP 587.

#### Scenario: IP fija
- **WHEN** la instancia se para y se vuelve a arrancar
- **THEN** conserva la IP de `instance_public_ip` y CloudFront sigue sirviendo la web

