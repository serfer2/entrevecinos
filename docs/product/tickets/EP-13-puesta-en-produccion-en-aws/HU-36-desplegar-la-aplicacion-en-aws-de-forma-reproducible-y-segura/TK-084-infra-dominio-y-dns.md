# TK-084 · Infraestructura: DNS de `entrevecinos.org` en Route 53, certificado y autenticación del correo

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/domain/` (nuevo), `infra/aws/modules/mail/`, `infra/aws/envs/prod/`; servidores de nombres del dominio en Dinahosting (paso manual único) |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-078, TK-083 |
| **Referencias** | Route 53 «Making Route 53 the DNS service for a domain that's in use»; ACM «DNS validation»; SES «Easy DKIM» y «Custom MAIL FROM domain»; RFC 7489 (DMARC), RFC 8659 (CAA) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El proyecto tiene el dominio `entrevecinos.org`, registrado en Dinahosting y con su DNS allí (`ns{,2,3,4}.dinahosting.com`). La web no tiene contenido propio: solo un `A` a `82.98.135.43` (página de Dinahosting) y algunos registros de correo creados a mano, uno de ellos mal (el DMARC está publicado en la raíz en lugar de en `_dmarc`, y solo hay uno de los cinco `CAA`).

Decisiones tomadas:
- **El DNS pasa a Amazon Route 53**, gestionado entero por Terraform: certificado, correo, políticas y registros de la web se crean y validan solos, sin copiar valores a mano.
- **El dominio sigue registrado en Dinahosting** (renovación, titular y bloqueo de transferencia allí). El único paso manual es cambiar sus servidores de nombres por los de Route 53, una sola vez.
- La **web principal es `https://entrevecinos.org`**; `www.entrevecinos.org` redirige a ella. La raíz apunta a CloudFront con un registro **alias** de Route 53 (TK-087).
- El correo de la aplicación sale de `no-reply@entrevecinos.org` por SES, autenticado con DKIM, SPF y DMARC.

**Objetivo:** crear la zona alojada de Route 53 con todos los registros de correo y de políticas, delegar el dominio en ella desde Dinahosting, y emitir el certificado HTTPS de `entrevecinos.org` y `www` y verificar el dominio en SES de forma automática.

## 2. Alcance

**Incluye**
- **Fase 0 — Preparación en Dinahosting** (manual, sin depender de AWS):
  1. Renovación automática del dominio activada.
  2. Bloqueo de transferencia activado.
  3. Privacidad del titular (WHOIS) activada, si Dinahosting la ofrece para `.org`.
  4. **DNSSEC desactivado** en Dinahosting antes del cambio de servidores de nombres (hoy no hay registro `DS`; si estuviera activo, el dominio dejaría de resolver al apuntar a Route 53).
  5. Redirección web o página de aparcamiento de Dinahosting: no hace falta tocarlas; dejan de aplicarse al cambiar los servidores de nombres.
- **Zona alojada pública** `aws_route53_zone` `entrevecinos.org` con `prevent_destroy`; salida `name_servers` con los 4 servidores de nombres.
- **Registros gestionados por Terraform** en la zona (`aws_route53_record`, TTL 300 durante la puesta en marcha y 3600 después, asumido):

  | Nombre | Tipo | Valor | Para qué |
  |---|---|---|---|
  | `entrevecinos.org` | `TXT` | `"v=spf1 -all"` | La raíz no envía correo directamente |
  | `_dmarc.entrevecinos.org` | `TXT` | `"v=DMARC1; p=none; adkim=s; aspf=r"` | DMARC en observación; endurecer en §8 |
  | `entrevecinos.org` | `CAA` | `0 issue "amazon.com"`, `0 issue "amazontrust.com"`, `0 issue "awstrust.com"`, `0 issue "amazonaws.com"`, `0 issuewild ";"` | Solo Amazon emite certificados; ningún comodín |
  | `_<hash>.entrevecinos.org`, `_<hash>.www.entrevecinos.org` | `CNAME` | Valores de `domain_validation_options` del certificado | Validación y renovación del certificado |
  | `<token>._domainkey.entrevecinos.org` (×3) | `CNAME` | `<token>.dkim.amazonses.com` | DKIM de SES |
  | `mail.entrevecinos.org` | `MX` | `10 feedback-smtp.eu-north-1.amazonses.com` | MAIL FROM (rebotes) |
  | `mail.entrevecinos.org` | `TXT` | `"v=spf1 include:amazonses.com -all"` | SPF del MAIL FROM |

  Los registros `A`/`AAAA` alias de la raíz y de `www` hacia CloudFront se crean en TK-087.
- **Certificado ACM** en `us-east-1` (región obligatoria para CloudFront; proveedor `aws.us_east_1`) para `entrevecinos.org` con nombre alternativo `www.entrevecinos.org`, validación por DNS con los registros anteriores y `aws_acm_certificate_validation`. La renovación anual es automática mientras los registros existan.
- **Identidad de dominio de SES** `entrevecinos.org` con Easy DKIM RSA 2048, asociada al *configuration set* de TK-083, y **dominio MAIL FROM** `mail.entrevecinos.org` con `behavior_on_mx_failure = USE_DEFAULT_VALUE`.
- **Paso manual único — delegación:** en el panel de Dinahosting, sustituir los servidores de nombres del dominio por los 4 de la salida `name_servers` (procedimiento detallado en `infra/aws/README.md`, TK-093).
- **Limpieza opcional** de la zona antigua de Dinahosting una vez delegado el dominio, para evitar confusiones (ya no se consulta).
- Actualización de `MAIL_FROM` de producción a `"EntreVecinos <no-reply@entrevecinos.org>"`.

**No incluye**
- Registros de la web, distribución de CloudFront y redirección de `www` (TK-087).
- Transferir el **registro** del dominio a Route 53 Domains (ver §8).
- DNSSEC en Route 53 (ver §8).
- Buzón para recibir correo en `entrevecinos.org` (no hay `MX` en la raíz; ver §8).

## 3. Requisitos técnicos

- **Orden de aplicación:**
  1. `terraform apply` crea la zona y todos los registros (incluidos los de validación), el certificado y la identidad de SES, sin esperar a la validación (`aws_acm_certificate_validation` en un segundo paso, p. ej. con una variable `wait_for_validation = false` la primera vez; asumido).
  2. Cambio manual de servidores de nombres en Dinahosting.
  3. Propagación de la delegación: el registro de `.org` la publica en minutos, pero los *resolvers* pueden tener en caché los NS antiguos hasta que caduque su TTL (hasta 1-2 días).
  4. Segundo `terraform apply`: `aws_acm_certificate_validation` espera a que ACM vea los registros (`timeouts { create = "2h" }`); SES verifica DKIM y MAIL FROM por su cuenta.
- Mientras no exista TK-087, `entrevecinos.org` no resuelve a ninguna web: es aceptable porque hoy solo muestra la página de Dinahosting.
- DMARC con `adkim=s`: el `From` (`entrevecinos.org`) coincide exactamente con el dominio DKIM que firma SES; `aspf=r` porque el MAIL FROM es el subdominio `mail.`.
- La política de TK-085 (rol de la instancia) restringe `ses:SendEmail` a la identidad `entrevecinos.org`.
- Ningún registro se crea a mano en la consola de Route 53: todo cambio pasa por Terraform (un `terraform plan` limpio demuestra que no hay deriva).

## 4. Criterios de aceptación

**AC1 — Dominio delegado en Route 53 (HU-36 AC1)**
- **Given** los servidores de nombres cambiados en Dinahosting
- **When** consulto `dig NS entrevecinos.org` y la delegación desde los servidores de `.org` (`dig +trace`)
- **Then** responden los 4 servidores de Route 53 de la zona, y `dig SOA entrevecinos.org` devuelve el SOA de Route 53

**AC2 — Certificado emitido (HU-36 AC2)**
- **Given** la delegación propagada
- **When** consulto el certificado en ACM (`us-east-1`)
- **Then** su estado es `ISSUED` y cubre `entrevecinos.org` y `www.entrevecinos.org`, sin haber creado ningún registro a mano

**AC3 — Dominio verificado en SES**
- **Given** la delegación propagada
- **When** consulto la identidad `entrevecinos.org`
- **Then** está verificada, DKIM está `SUCCESS` y MAIL FROM `SUCCESS`

**AC4 — Correo autenticado**
- **Given** un correo de validación enviado a una dirección verificada (o cualquiera, si ya no hay *sandbox*)
- **When** veo sus cabeceras originales en el cliente de correo
- **Then** `spf=pass`, `dkim=pass` y `dmarc=pass` para `entrevecinos.org`

**AC5 — Políticas publicadas y sin deriva**
- **Given** la zona de Route 53
- **When** consulto con `dig` y ejecuto `terraform plan`
- **Then** existen los 5 registros `CAA`, el SPF de la raíz y el DMARC **en `_dmarc`** (no en la raíz), y el plan no muestra cambios

**AC6 — Fase 0 completada**
- **Given** el panel del dominio en Dinahosting
- **When** lo reviso
- **Then** la renovación automática y el bloqueo de transferencia están activos y DNSSEC está desactivado antes del cambio de servidores de nombres

## 5. Plan de tareas

0. Fase 0 en Dinahosting (AC6).
1. Módulo `domain`: zona alojada, registros de políticas y salida `name_servers`.
2. Certificado ACM en `us-east-1` y registros de validación.
3. Identidad de dominio de SES, DKIM y MAIL FROM con sus registros.
4. Primer `apply`.
5. Cambio de servidores de nombres en Dinahosting y espera de la propagación.
6. Segundo `apply` con la validación; comprobaciones de AC1 a AC5.

## 6. Verificación

```bash
make tf-apply                                    # crea zona y registros; muestra name_servers
# Dinahosting: cambiar los servidores de nombres por los 4 de la salida
dig +short NS entrevecinos.org                   # los 4 de Route 53
dig +trace NS entrevecinos.org | tail -8         # delegación desde los servidores de .org
dig +short TXT _dmarc.entrevecinos.org           # DMARC en su sitio
dig +short TXT entrevecinos.org                  # solo "v=spf1 -all"
dig +short CAA entrevecinos.org                  # 5 registros
dig +short CNAME <token1>._domainkey.entrevecinos.org
make tf-apply                                    # espera la validación del certificado
aws acm describe-certificate --certificate-arn <arn> --region us-east-1 --profile entrevecinos --query 'Certificate.Status'
aws sesv2 get-email-identity --email-identity entrevecinos.org --profile entrevecinos \
  --query '{v:VerifiedForSendingStatus,dkim:DkimAttributes.Status,mf:MailFromAttributes.MailFromDomainStatus}'
make tf-plan                                     # sin cambios
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Procedimiento de delegación documentado en `infra/aws/README.md`.
- [ ] `make tf-lint` sin errores.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Coste:** la zona alojada cuesta 0,50 USD/mes más las consultas (céntimos con poco tráfico; las consultas a registros alias de CloudFront no se cobran). Comprobar si el plan gratuito de CloudFront (TK-087) incluye el DNS de Route 53.
- **Control del DNS ligado a la cuenta de AWS:** quien comprometa la cuenta controla el DNS. El registro del dominio sigue en Dinahosting, así que siempre se puede volver a sus servidores de nombres. `prevent_destroy` en la zona evita borrarla por error con Terraform.
- **Hueco de propagación:** durante el cambio, algunos *resolvers* consultan aún Dinahosting y otros Route 53. Como la web todavía no está en producción, no afecta a usuarios; con la web ya publicada habría que replicar antes sus registros en Route 53.
- **Transferir también el registro a Route 53 Domains:** dejaría todo en AWS, pero no es necesario y depende de que el plan del proyecto lo admita. Se mantiene en Dinahosting.
- **DNSSEC:** Route 53 puede firmar la zona (necesita una clave KMS en `us-east-1`, ≈ 1 USD/mes, y publicar el `DS` en Dinahosting). Recomendado como mejora cuando el resto esté estable.
- **Endurecer DMARC:** empezar con `p=none` y, tras unas semanas sin fallos, pasar a `p=quarantine` y luego `p=reject`. Para recibir informes (`rua=`) hace falta un buzón; si es de otro dominio, ese dominio debe autorizarlo.
- **Sin buzón en el dominio:** nadie recibe las respuestas a `no-reply@`. Si se quiere un `contacto@entrevecinos.org`, añadir con Terraform el `MX` del proveedor de correo en la raíz; no interfiere con SES.
- **Origen cifrado (TK-087 §8):** con Route 53, Caddy puede obtener un certificado de Let's Encrypt para `origin.entrevecinos.org` por desafío DNS-01 de forma automática; habría que añadir `0 issue "letsencrypt.org"` al `CAA`.
