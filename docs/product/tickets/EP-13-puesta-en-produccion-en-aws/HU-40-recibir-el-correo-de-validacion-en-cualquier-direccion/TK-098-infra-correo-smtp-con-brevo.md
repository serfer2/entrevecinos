# TK-098 · Infraestructura: correo de producción por SMTP con Brevo

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura |
| **Componente** | `infra/aws/modules/domain/` (registros DNS), `infra/aws/modules/network/` (salida 587), `infra/docker-compose.prod.yml`, `infra/prod/deploy.sh`, Parameter Store, `infra/aws/README.md` |
| **Historia** | HU-40 Recibir el correo de validación en cualquier dirección (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-096 |
| **Referencias** | `apps/api` (`MAIL_BACKEND=smtp`, `SMTP_*`, STARTTLS obligatorio en producción); TK-079 (grupo de seguridad: solo sale por 443); TK-084 (SPF `v=spf1 -all` en la raíz, DMARC `p=none; adkim=s`); TK-086 (secretos solo por entorno); [guía técnica de Brevo](https://www.captaindns.com/en/blog/brevo-transactional-email-technical-guide) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-096 elige Brevo como proveedor de correo de producción. La API ya admite SMTP con STARTTLS (`MAIL_BACKEND=smtp`, el mismo adaptador que usa Mailpit en local), así que no hay cambios de código. Hay que autenticar el dominio en Brevo, llevar las credenciales a los contenedores como el resto de secretos, permitir la salida SMTP de la instancia y cambiar la configuración de producción.

**Objetivo:** que la API envíe por `smtp-relay.brevo.com:587` con STARTTLS como `no-reply@entrevecinos.org`, con DKIM alineado con el dominio y SES intacto como vuelta atrás.

## 2. Alcance

**Incluye**
- **Autenticación del dominio en Brevo**, con registros en Route 53 gestionados por Terraform (`modules/domain` o `modules/mail`). Los valores se copian de la cuenta de Brevo, no de ejemplos:
  - **verificación:** TXT `brevo-code:<código>` en `entrevecinos.org`. **Route 53 solo admite un conjunto TXT por nombre**, así que va en el mismo recurso que el SPF de la raíz, como un segundo valor;
  - **DKIM:** los dos CNAME que da Brevo (asumido: `brevo1._domainkey` y `brevo2._domainkey`, 2048 bits). Firman con `d=entrevecinos.org`, lo que cumple DMARC con `adkim=s`;
  - **SPF:** la raíz publica hoy `v=spf1 -all`, porque SES usa `MAIL FROM` en `mail.entrevecinos.org`. Si Brevo envía con su propio dominio de rebotes, DMARC pasa por DKIM y el SPF de la raíz no se evalúa. Si Brevo exige SPF, pasa a `v=spf1 include:spf.brevo.com -all`. Hay que decidirlo según lo que pida Brevo al autenticar el dominio;
  - **DMARC:** se mantiene el actual (`p=none`); Brevo exige que exista.
- **Secretos:**
  - `/entrevecinos/prod/smtp/username` y `/entrevecinos/prod/smtp/password` (`SecureString`), creados a mano con `aws ssm put-parameter` (Terraform no conoce los valores; así no quedan en el estado);
  - `deploy.sh` los lee en la misma llamada que el resto y los exporta solo por entorno;
  - el rol de la instancia ya puede leer `/entrevecinos/prod/*`.
- **Compose de producción** (`api`):
  - `MAIL_BACKEND: smtp`, `SMTP_HOST: smtp-relay.brevo.com`, `SMTP_PORT: 587`, `SMTP_STARTTLS: "true"`;
  - `SMTP_USERNAME` y `SMTP_PASSWORD` desde el entorno de `deploy.sh` (`${…:?Lo define deploy.sh}`);
  - `MAIL_FROM` sin cambios;
  - se retiran `SES_REGION` y `SES_CONFIGURATION_SET`.
- **Red:** regla de salida TCP 587 en el grupo de seguridad de la instancia (`modules/network`). Destino `0.0.0.0/0`, porque Brevo no publica rangos de entrada para su *relay* (asumido). La red `egress` de Compose ya da salida a la API.
- **SES como vuelta atrás:** se conservan la identidad, DKIM, `MAIL FROM`, el *configuration set* y el permiso `ses:SendEmail`. Volver es cambiar las variables del Compose, `make tf-apply` y desplegar. Las alarmas de reputación de SES quedan sin datos (sin avisos).
- **`infra/aws/README.md`:**
  - «Secretos»: los dos parámetros nuevos y cómo crearlos o rotarlos;
  - «DNS»: los registros de Brevo;
  - «Puesta en marcha»: el orden, porque los parámetros se crean antes del `apply` y el despliegue;
  - el *runbook* de correo: comprobar el envío, rotar la clave SMTP y volver a SES;
  - «Costes»: Brevo gratis hasta 300 al día.

**No incluye**
- Cambios en el código de la API: el adaptador SMTP ya existe y está probado.
- Webhooks de rebotes de Brevo (mejora posterior; Brevo gestiona su propia lista de supresión).

## 3. Requisitos técnicos

- STARTTLS obligatorio: la configuración de la API lo exige en producción.
- Credenciales nunca en el repositorio, el estado de Terraform, ficheros de la instancia ni registros (`deploy.sh` sin traza).
- `make tf-plan`: solo cambian el TXT de la raíz, los CNAME de DKIM, el grupo de seguridad y el documento de SSM; ningún registro de la web ni de SES.
- `make tf-lint` y `make shellcheck` sin avisos.

## 4. Criterios de aceptación

**AC1 — Correo por Brevo (HU-40 AC1)**
- **Given** producción con `MAIL_BACKEND=smtp` hacia Brevo
- **When** me registro con dos direcciones no verificadas de proveedores distintos (asumido: Gmail y Outlook)
- **Then** recibo el enlace en la bandeja de entrada; las cabeceras muestran `dkim=pass` con `d=entrevecinos.org` y `dmarc=pass`

**AC2 — Dominio autenticado en Brevo**
- **Given** la cuenta de Brevo
- **When** consulto el dominio `entrevecinos.org` en *Senders, domains & dedicated IPs*
- **Then** figura autenticado (código de verificación, DKIM y DMARC correctos)

**AC3 — Secretos y red**
- **Given** la instancia
- **When** reviso `/opt/entrevecinos`, la salida de `deploy.sh` y el grupo de seguridad
- **Then** las credenciales SMTP no están en ningún fichero ni registro, y la única salida nueva es TCP 587

**AC4 — Vuelta atrás documentada**
- **Given** `infra/aws/README.md`
- **When** consulto cómo volver a SES
- **Then** encuentro los pasos (variables del Compose, `make tf-apply` y despliegue) y SES sigue configurado

## 5. Plan de tareas

1. Autenticación del dominio en Brevo: valores de la cuenta; registros TXT y CNAME en Terraform.
2. Parámetros de las credenciales; `deploy.sh` y Compose de producción.
3. Regla de salida 587.
4. `make tf-lint`, `make shellcheck`, `make tf-plan`, `make tf-apply` y despliegue.
5. Pruebas de extremo a extremo y documentación.

## 6. Verificación

```bash
dig +short TXT entrevecinos.org                         # SPF y brevo-code en el mismo conjunto
dig +short CNAME brevo1._domainkey.entrevecinos.org
aws ssm get-parameters --profile entrevecinos --names /entrevecinos/prod/smtp/username /entrevecinos/prod/smtp/password \
  --query 'Parameters[].[Name,Type]'                    # sin --with-decryption
aws ec2 describe-security-group-rules --profile entrevecinos \
  --filters Name=group-id,Values=<grupo de la instancia> --query 'SecurityGroupRules[?IsEgress].[IpProtocol,FromPort,CidrIpv4]'
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Ninguna credencial en el repositorio ni en el estado.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **SPF de la raíz:** depende de lo que exija Brevo (ver Alcance); con DKIM alineado, DMARC pasa sin él.
- **Salida SMTP abierta:** el puerto 587 a cualquier destino amplía la salida de la instancia; un proceso comprometido podría enviar correo por otros servidores. Mitigación: solo la API tiene la red `egress`; restringir el destino si Brevo publica rangos.
- **Límite de 300 al día:** al agotarlo, Brevo rechaza los envíos y salta la alarma de fallos de envío (TK-097).
- **Dependencia externa:** alta y claves fuera de Terraform; la rotación de la clave SMTP es manual (nueva clave en Brevo, `put-parameter --overwrite` y desplegar).
