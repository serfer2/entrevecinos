## Why

HU-36: la web se publica en `https://entrevecinos.org` y el correo sale de `no-reply@entrevecinos.org`, así que hacen falta un certificado HTTPS y un dominio autenticado en SES (HU-36 AC1 y AC2). Gestionar el DNS en Route 53 con Terraform permite crear y validar ambos solos, sin copiar registros a mano. Ticket: `docs/product/tickets/EP-13-puesta-en-produccion-en-aws/HU-36-desplegar-la-aplicacion-en-aws-de-forma-reproducible-y-segura/TK-084-infra-dominio-y-dns.md`.

## What Changes

- `modules/domain` (nuevo): zona alojada `entrevecinos.org` protegida contra borrado; registros de políticas (SPF de la raíz, DMARC en `_dmarc` y 5 `CAA`); certificado de ACM en `us-east-1` para `entrevecinos.org` y `www`, con sus registros de validación y una espera opcional de la validación (`wait_for_certificate_validation`).
- `modules/mail`: identidad de dominio de SES con Easy DKIM RSA 2048 y el *configuration set* de TK-083, dominio MAIL FROM `mail.entrevecinos.org` y sus registros (3 `CNAME` de DKIM, `MX` y SPF).
- Salidas `name_servers`, `certificate_arn` y `ses_domain_identity_arn`.
- `infra/aws/README.md`: procedimiento de delegación desde Dinahosting, sección «DNS» y remitente de producción.

## Capabilities

### New Capabilities
- `aws-domain`: DNS del dominio en Route 53, certificado HTTPS y autenticación del correo.

### Modified Capabilities

## Impact

- Rutas de infraestructura: `infra/aws/modules/domain/`, `infra/aws/modules/mail/`, `infra/aws/envs/prod/` («Puesta en marcha», «DNS» y «Costes» de `infra/aws/README.md`).
- Crea recursos en AWS (zona alojada, 0,50 USD/mes). Requiere cambiar a mano los servidores de nombres en Dinahosting una vez.
