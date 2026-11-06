# aws-domain Specification

## Purpose
DNS de `entrevecinos.org` en Route 53, gestionado entero por Terraform con el registro del dominio en Dinahosting: políticas de correo y de certificados, certificado HTTPS de ACM para la raíz y `www`, e identidad de dominio de SES con DKIM y MAIL FROM.
## Requirements
### Requirement: Zona de Route 53 gestionada por Terraform
Terraform SHALL crear la zona alojada pública `entrevecinos.org`, protegida contra borrado, y MUST exponer sus 4 servidores de nombres como salida `name_servers`. Ningún registro de la zona SHALL crearse a mano.

#### Scenario: Delegación
- **WHEN** los servidores de nombres del dominio en Dinahosting son los de la salida `name_servers` y consulto `dig NS entrevecinos.org`
- **THEN** responden los 4 servidores de Route 53 de la zona

#### Scenario: Sin deriva
- **WHEN** ejecuto `make tf-plan` tras aplicar
- **THEN** no hay cambios

### Requirement: Políticas de correo y de certificados
La zona SHALL publicar `"v=spf1 -all"` en la raíz, el DMARC `"v=DMARC1; p=none; adkim=s; aspf=r"` en `_dmarc.entrevecinos.org` (no en la raíz) y 5 registros `CAA` que solo autorizan a Amazon y prohíben los comodines.

#### Scenario: DMARC en su sitio
- **WHEN** consulto `dig TXT _dmarc.entrevecinos.org` y `dig TXT entrevecinos.org`
- **THEN** el DMARC está en `_dmarc` y la raíz solo tiene el SPF

### Requirement: Certificado HTTPS
Terraform SHALL solicitar en `us-east-1` un certificado de ACM para `entrevecinos.org` con `www.entrevecinos.org` como nombre alternativo, validado por DNS con registros de la zona, que se renueva solo mientras existan.

#### Scenario: Certificado emitido
- **WHEN** la delegación se ha propagado y aplico con `wait_for_certificate_validation = true`
- **THEN** el certificado está `ISSUED` y cubre los dos nombres

### Requirement: Dominio autenticado en SES
Terraform SHALL crear la identidad de dominio `entrevecinos.org` en SES con Easy DKIM RSA 2048 y el *configuration set* `entrevecinos-prod`, y el dominio MAIL FROM `mail.entrevecinos.org` con su `MX` y su SPF, todo con registros de la zona.

#### Scenario: Dominio verificado
- **WHEN** la delegación se ha propagado y consulto la identidad `entrevecinos.org`
- **THEN** está verificada para enviar, con DKIM y MAIL FROM en `SUCCESS`

#### Scenario: Correo autenticado
- **WHEN** reviso las cabeceras de un correo enviado desde `no-reply@entrevecinos.org`
- **THEN** `spf=pass`, `dkim=pass` y `dmarc=pass`

