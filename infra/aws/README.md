# Producción en AWS

Guía de operación de producción de EntreVecinos y registro de sus decisiones de arquitectura. La infraestructura se define con Terraform en este directorio y se despliega en el proyecto de AWS `995006761619`, región `eu-north-1`. Todo cambio en `infra/aws/`, `infra/prod/`, `infra/docker-compose.prod.yml` o `.github/workflows/` debe actualizar esta guía en el mismo cambio (ver `AGENTS.md`, §Convenciones).

> **Estado:** en construcción. La Épica 13 (`docs/product/tickets/EP-13-puesta-en-produccion-en-aws/`) completa cada sección con el ticket indicado. Ya están escritos el límite de gasto y la base de Terraform (TK-078), la red (TK-079), el registro de imágenes y el bucket de fotografías (TK-080), PostgreSQL con sus copias (TK-082), SES con los secretos (TK-083) el DNS con el certificado (TK-084) y la instancia (TK-085); el despliegue y CloudFront llegan en TK-086 y TK-087.

## Estructura

```
infra/aws/
├── bootstrap/          bucket del estado de Terraform (estado local; se aplica una vez)
├── envs/prod/          composición de producción: backend S3, proveedores, variables y salidas
│   └── prod.tfvars.example   copia a prod.tfvars (no se versiona)
├── modules/
│   ├── private-bucket/ bucket S3 privado con los valores seguros comunes
│   ├── budget/         presupuesto mensual con avisos (TK-078)
│   ├── compute/        instancia EC2 endurecida, su rol, Session Manager y Patch Manager (TK-085)
│   ├── network/        VPC, subred pública, grupo de seguridad y flow logs (TK-079)
│   ├── storage/        repositorios ECR y bucket de imágenes (TK-080)
│   ├── database/       volumen de PostgreSQL, snapshots, bucket de copias y contraseñas (TK-082)
│   ├── domain/         zona de Route 53, políticas de correo y certificado HTTPS (TK-084)
│   └── mail/           SES (configuration set, dominio con DKIM y MAIL FROM) y secreto de los JWT (TK-083, TK-084)
├── .tflint.hcl         reglas de tflint
└── .checkov.yaml       comprobaciones de checkov omitidas, con su motivo
infra/prod/             ficheros que se copian a la instancia (TK-082, TK-086)
├── initdb/10-roles.sh  roles de PostgreSQL
├── backup.sh           copia de PostgreSQL a S3
└── systemd/            servicio y temporizador de las copias
```

Versiones fijadas: Terraform 1.16.7 (`>= 1.11` en el código), proveedor `hashicorp/aws` `~> 6.70.0` y `hashicorp/random` `~> 3.9`, con `.terraform.lock.hcl` versionado para Linux y macOS (amd64 y arm64). Todo se ejecuta en contenedores con `make`:

| Comando | Qué hace |
|---|---|
| `make tf-bootstrap` | Crea el bucket del estado (una sola vez) |
| `make tf-init` | Inicializa `envs/prod` con el estado en S3 |
| `make tf-plan` / `make tf-apply` | Muestra o aplica los cambios con `prod.tfvars` (`apply` pide confirmación) |
| `make tf-output` | Muestra las salidas |
| `make tf-lint` | `terraform fmt` y `validate`, tflint y checkov; no necesita credenciales |

Las credenciales temporales de `aws login` se pasan al contenedor por entorno (`aws configure export-credentials`), sin escribirlas en disco. Recursos de CloudFront que AWS exige en `us-east-1` (certificado y WAF) usan el proveedor `aws.us_east_1`; el resto, `eu-north-1`. Todos llevan las etiquetas `Project = entrevecinos`, `Environment = prod` y `ManagedBy = terraform`.

## Puesta en marcha

Requisitos: Docker, AWS CLI v2 y una sesión del proyecto (`aws login --profile entrevecinos`; caduca y hay que repetirla).

1. **Límite de gasto (manual, antes que nada).** El propietario del proyecto fija **40 € al mes** en AWS Settings > Billing > *Spend limit*. Si el panel solo admite USD, se usa el equivalente redondeado hacia abajo y se anota en «Costes». Al alcanzarlo, AWS pausa el proyecto (las operaciones fallan con `AccessDenied` y la web puede caer).
2. **Estado de Terraform:** `make tf-bootstrap` crea `entrevecinos-tfstate-995006761619` (privado, cifrado, versionado). Su estado queda en `infra/aws/bootstrap/terraform.tfstate`, fuera del repositorio: consérvalo.
3. **Variables:** `cp infra/aws/envs/prod/prod.tfvars.example infra/aws/envs/prod/prod.tfvars` y ajusta el correo de avisos, el importe del presupuesto y los destinatarios de prueba de SES.
4. **Infraestructura:** `make tf-init`, `make tf-plan` y `make tf-apply`. Un segundo `make tf-plan` no debe mostrar cambios.
5. **Pasos manuales tras el `apply`:**
   - cada destinatario de `ses_test_recipients` recibe un correo de AWS y debe pulsar el enlace de verificación;
   - los avisos de AWS Budgets llegan directamente al correo configurado (no necesitan confirmación);
   - **delegación del dominio** en Dinahosting (ver «DNS»), y después `wait_for_certificate_validation = true` en `prod.tfvars` y otro `make tf-apply`.
6. **Salida del *sandbox* de SES**, cuando `https://entrevecinos.org` ya responda (TK-087):

   ```bash
   aws sesv2 put-account-details --profile entrevecinos \
     --mail-type TRANSACTIONAL --website-url https://entrevecinos.org \
     --contact-language ES --additional-contact-email-addresses <correo-de-contacto> \
     --use-case-description "Correo transaccional de EntreVecinos (validación de la cuenta al registrarse). Sin envíos comerciales; rebotes y quejas gestionados con un configuration set y la lista de supresión de la cuenta."
   aws sesv2 get-account --profile entrevecinos --query '{prod:ProductionAccessEnabled,review:Details.ReviewDetails}'
   ```

   Mientras AWS no la apruebe, SES solo envía a direcciones verificadas y como máximo 200 correos al día.

*Pendiente: TK-086 y TK-087* (despliegue y CloudFront).

## Despliegue

*Pendiente: TK-086 y TK-090.* Compose de producción, `deploy.sh`, primer despliegue manual por SSM, despliegue continuo desde GitHub Actions y vuelta atrás.

## DNS

El dominio `entrevecinos.org` sigue **registrado en Dinahosting** (renovación automática y bloqueo de transferencia activos, DNSSEC desactivado). Su **DNS está en Route 53**, en una zona alojada que gestiona entera Terraform (`modules/domain`, con `prevent_destroy`). **No se crean registros a mano** en la consola: un `make tf-plan` sin cambios demuestra que no hay deriva.

| Nombre | Tipo | Valor | Para qué |
|---|---|---|---|
| `entrevecinos.org` | `TXT` | `v=spf1 -all` | La raíz no envía correo |
| `_dmarc.entrevecinos.org` | `TXT` | `v=DMARC1; p=none; adkim=s; aspf=r` | DMARC en observación |
| `entrevecinos.org` | `CAA` | `amazon.com`, `amazontrust.com`, `awstrust.com`, `amazonaws.com` e `issuewild ";"` | Solo Amazon emite certificados; ningún comodín |
| `_<hash>.entrevecinos.org`, `_<hash>.www.entrevecinos.org` | `CNAME` | Validación de ACM | Emisión y renovación del certificado |
| `<token>._domainkey.entrevecinos.org` (×3) | `CNAME` | `<token>.dkim.amazonses.com` | DKIM de SES |
| `mail.entrevecinos.org` | `MX` | `10 feedback-smtp.eu-north-1.amazonses.com` | MAIL FROM (rebotes) |
| `mail.entrevecinos.org` | `TXT` | `v=spf1 include:amazonses.com -all` | SPF del MAIL FROM |

Los alias de la raíz y de `www` hacia CloudFront llegan en TK-087. TTL de 300 s durante la puesta en marcha; se subirá a 3600 (`dns_ttl`) cuando esté estable.

- **Certificado:** ACM en `us-east-1` (lo exige CloudFront) para `entrevecinos.org` y `www.entrevecinos.org`, validado por DNS. Se renueva solo mientras existan sus registros.
- **Correo:** identidad de dominio de SES con Easy DKIM RSA 2048 y el *configuration set* `entrevecinos-prod`; MAIL FROM `mail.entrevecinos.org`. Remitente de producción: `MAIL_FROM="EntreVecinos <no-reply@entrevecinos.org>"` (lo fija el Compose de producción, TK-086). Nadie lee las respuestas: no hay `MX` en la raíz.

**Delegación desde Dinahosting** (una sola vez):

1. `make tf-apply` con `wait_for_certificate_validation = false` crea la zona y todos sus registros sin esperar a ACM.
2. `make tf-output` muestra `name_servers` (4 servidores `ns-….awsdns-…`).
3. En Dinahosting, **Dominios → entrevecinos.org → Servidores DNS**: servidores personalizados, los 4 de `name_servers` sin el punto final, en lugar de `ns{,2,3,4}.dinahosting.com`. La zona antigua de Dinahosting deja de consultarse.
4. Propagación: `dig +trace NS entrevecinos.org` muestra la delegación desde `.org` en minutos; los *resolvers* pueden tardar hasta 1-2 días en olvidar los servidores antiguos.
5. `wait_for_certificate_validation = true` en `prod.tfvars` y `make tf-apply`: espera (hasta 2 h) a que el certificado esté `ISSUED`. SES verifica DKIM y MAIL FROM por su cuenta.

Comprobaciones:

```bash
dig +short NS entrevecinos.org; dig +short SOA entrevecinos.org    # servidores de Route 53
dig +short TXT _dmarc.entrevecinos.org; dig +short CAA entrevecinos.org
aws acm list-certificates --region us-east-1 --profile entrevecinos \
  --query "CertificateSummaryList[?DomainName=='entrevecinos.org'].Status"
aws sesv2 get-email-identity --email-identity entrevecinos.org --profile entrevecinos \
  --query '{envio:VerifiedForSendingStatus,dkim:DkimAttributes.Status,mailFrom:MailFromAttributes.MailFromDomainStatus}'
```

**Volver atrás:** poner de nuevo `ns{,2,3,4}.dinahosting.com` en Dinahosting. La zona de Route 53 no se borra (`prevent_destroy`).

*Pendiente: TK-087* (alias de la web y redirección de `www`).

## Secretos

Todos los secretos viven en SSM Parameter Store como `SecureString` (nivel estándar, gratuito, cifrados con la clave gestionada `aws/ssm`), bajo `/entrevecinos/prod/`. No se usa Secrets Manager.

| Parámetro | Contenido | Ticket |
|---|---|---|
| `/entrevecinos/prod/jwt-secret` | Clave de firma de los JWT (64 caracteres) | TK-083 |
| `/entrevecinos/prod/db/postgres-password` | Superusuario de PostgreSQL (solo administración) | TK-082 |
| `/entrevecinos/prod/db/owner-password` | `entrevecinos_owner` (migraciones y copias) | TK-082 |
| `/entrevecinos/prod/db/app-password` | `entrevecinos_app` (la API) | TK-082 |
| `/entrevecinos/prod/db/{host,port,name}` | Conexión (`String`, no secretos): `db`, `5432`, `entrevecinos` | TK-082 |

- Los valores se generan con `ephemeral "random_password"` y se escriben con argumentos de solo escritura (`value_wo`): **no quedan en el estado de Terraform**.
- No tienen rotación automática. Para rotar: sube `jwt_secret_version` o `db_password_version` en `prod.tfvars`, `make tf-apply` y vuelve a desplegar (TK-086 aplica las contraseñas nuevas a PostgreSQL y recrea los contenedores). Rotar el secreto de los JWT invalida todas las sesiones.
- Para consultar uno (solo administración): `aws ssm get-parameter --name <nombre> --with-decryption --profile entrevecinos`.

*Pendiente: TK-086* (cómo llegan a los contenedores, solo por entorno).

## Operación

### Instancia de aplicación (TK-085)

Una sola instancia `entrevecinos-prod-app` (`t4g.small`, arm64, Amazon Linux 2023) en `eu-north-1a`, con IP pública y el grupo de seguridad que solo admite HTTP desde CloudFront. Ejecuta Docker Compose (TK-086).

- **Acceso solo con Session Manager:** sin par de claves, sin puerto 22 y con `sshd` desactivado. Cada sesión queda registrada en `/entrevecinos/prod/ssm-sessions` (30 días); se cierra tras 20 minutos inactiva y dura como máximo 60.

  ```bash
  aws ssm start-session --profile entrevecinos --target "$(make -s tf-output | sed -n 's/^instance_id = "\(.*\)"/\1/p')"
  ```

  Necesita el [Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) en el equipo. Sin él, se ejecutan comandos con Run Command (`aws ssm send-command --document-name AWS-RunShellScript …`) o se abre la sesión desde la consola de EC2 (*Connect* → *Session Manager*).
- **Endurecimiento:** IMDSv2 obligatorio (*hop limit* 2, para que los contenedores obtengan las credenciales del rol), volumen raíz `gp3` de 20 GB cifrado, protección contra la terminación y créditos de CPU `standard` (sin cargos por exceso; si la CPU se agota, la instancia se ralentiza).
- **Primer arranque** (`modules/compute/user-data.sh.tftpl`, registro en `/var/log/cloud-init-output.log`): actualiza el sistema e instala Docker (con `live-restore`, `no-new-privileges` y logs rotados), Compose v5.6.1 (con su SHA-256 comprobado), el agente de CloudWatch (se configura en TK-091) y `dnf-automatic`. Crea 1 GB de *swap*, el usuario `deploy` (sin *shell* ni grupo `docker`) y `/opt/entrevecinos` (750). Solo se ejecuta al crear la instancia: Terraform ignora sus cambios y los de la AMI.
- **Volumen de datos** de TK-082 adjunto y montado por UUID en `/srv/entrevecinos/postgres` (XFS, `nofail`). Se formatea solo si no tiene sistema de ficheros, y Docker no arranca si no está montado (`RequiresMountsFor`), así que PostgreSQL nunca escribe en el volumen raíz.
- **Parches:** `dnf-automatic` aplica a diario los de seguridad, y Patch Manager (`AWS-RunPatchBaseline`, `Install`) todos los domingos a las 04:00 UTC, reiniciando si hace falta (corte de minutos). Estado: `aws ssm describe-instance-patch-states --instance-ids <id> --profile entrevecinos`.
- **Recuperación:** la alarma `entrevecinos-prod-app-recover` recupera la instancia (mismo ID, IP y volúmenes) si falla el *status check* del sistema.
- **Rol `entrevecinos-prod-app`** (mínimo privilegio, validado con IAM Access Analyzer): `AmazonSSMManagedInstanceCore` y una política propia que permite:
  - `PutObject` y `GetObject` en el bucket de imágenes, y en `postgres/` del de copias (sin borrar);
  - `ses:SendEmail` con la identidad del dominio, el *configuration set* y, mientras haya *sandbox*, los destinatarios de prueba, solo con remitente `no-reply@entrevecinos.org`;
  - leer los parámetros de `/entrevecinos/prod/`. `AmazonSSMManagedInstanceCore` concede `ssm:GetParameter(s)` sobre `*`, así que la política deniega expresamente cualquier otro parámetro de la cuenta (solo quedan además los públicos de AWS, `/aws/*`);
  - descargar imágenes de los dos repositorios de ECR;
  - escribir en los grupos de logs `/entrevecinos/prod/app/*` y de sesiones, y publicar métricas en `Entrevecinos/Backup` y `CWAgent`.
- **Reemplazar la instancia** (nueva AMI, cambio de *user data*): procedimiento en TK-093.

### Base de datos y copias (TK-082)

PostgreSQL 16 corre como contenedor `db` en la instancia, con los datos en un volumen EBS propio (`entrevecinos-prod-postgres`, 10 GB, cifrado) que sobrevive a la instancia.

- **Roles** (`infra/prod/initdb/10-roles.sh`, idempotente): `postgres` (solo administración), `entrevecinos_owner` (propietario; solo migraciones) y `entrevecinos_app` (la API: `SELECT`, `INSERT`, `UPDATE`, `DELETE`; sin DDL ni `TRUNCATE`).
- **Copias con `pg_dump`** cada 6 horas (`entrevecinos-backup.timer` a las 00, 06, 12 y 18 UTC): `backup.sh` sube la copia en *streaming* a `s3://entrevecinos-backups-995006761619/postgres/AAAA/MM/DD/`, comprueba su tamaño y que `pg_restore --list` la lee, y publica la métrica `Entrevecinos/Backup BackupSucceeded`. Se conservan 30 días.
- **Snapshots** diarios del volumen a las 03:00 UTC con Data Lifecycle Manager; se conservan 7.
- **Copias protegidas:** la política del bucket deniega el borrado a todos salvo a los roles de `admin_role_arns`; la instancia solo escribe y lee.
- Copia a demanda (p. ej. antes de una migración destructiva): `sudo systemctl start entrevecinos-backup.service` en la instancia.

*Pendiente: TK-091 a TK-093* (registros, alarmas, restauración probada y *runbook*).

## Costes

- **Límite de gasto:** 40 €/mes en AWS Settings (manual, paso 1 de la puesta en marcha). Equivalente en USD anotado: **44 USD** (fijado el 2026-11-05).
- **Presupuesto** `entrevecinos-mensual` en AWS Budgets, igual al límite (`monthly_budget_usd`, 44 USD): avisos por correo al 50 %, 75 % y 90 % del gasto real y al 100 % del previsto.
- **Estimación** de la épica completa (sin alta disponibilidad, mientras el proyecto no escale): unos 20 USD/mes. Hasta TK-085 solo se pagan céntimos (S3, ECR, CloudWatch y el volumen de datos, ≈ 1 USD/mes) y la zona de Route 53 (0,50 USD/mes más las consultas; las de alias a CloudFront no se cobran).
- **Instancia** (TK-085): `t4g.small` ≈ 12 USD/mes más el volumen raíz de 20 GB (≈ 1,6 USD/mes). Entra en la capa gratuita del plan FREE, así que se paga con los créditos. Con créditos de CPU `standard` no hay cargos por exceso.

*Pendiente: TK-093* (estimación por servicio con la infraestructura completa).

## Decisiones de arquitectura

### Base de datos en la instancia (TK-082)

- **Qué:** PostgreSQL 16 en un contenedor de la instancia EC2, con volumen EBS propio, sin alta disponibilidad, en lugar de Amazon RDS.
- **Por qué:** **ahorro de costes mientras el proyecto no escale** (≈ 15 USD/mes menos, dentro del límite de 40 €/mes); no se necesita alta disponibilidad hasta que el proyecto sea maduro y tenga mucho tráfico.
- **Impacto:** RPO de 6 horas (sin recuperación a un punto en el tiempo), sin conmutación por error, mantenimiento de PostgreSQL a cargo del proyecto y base y aplicación en la misma máquina (si se compromete la instancia, se compromete la base).
- **Mitigaciones:** copias cada 6 horas comprobadas, alarma si falta una (TK-091), volumen separado que sobrevive a la instancia y usuario de aplicación sin privilegios.
- **Cuándo revisarla:** tráfico sostenido que satura la instancia, datos que no se pueden perder 6 horas o más de un servidor de aplicación.
- **Evolución:** migrar a Amazon RDS (`pg_dump` / `pg_restore`, nuevo `DATABASE_URL`, corte de minutos) y después Multi-AZ.

### Instancia única endurecida (TK-085)

- **Qué:** web, API, proxy y PostgreSQL en una instancia EC2 `t4g.small` con Docker Compose, en lugar de ECS Fargate con balanceador.
- **Por qué:** **coste, mientras el proyecto no escale** (≈ 12 USD/mes frente a 30-40 USD/mes de Fargate y ALB), dentro del límite de 40 €/mes.
- **Impacto:** la seguridad del sistema operativo queda a cargo del proyecto (parches, acceso y permisos), y la web y la API comparten host y rol: un fallo en la web daría acceso a las credenciales de la API. Sin alta disponibilidad: un fallo de la instancia corta el servicio hasta que se recupera.
- **Mitigaciones:** sin SSH (Session Manager con registro), IMDSv2, rol de mínimo privilegio, parches automáticos, recuperación automática y contenedores sin privilegios ni socket de Docker (TK-086).
- **Cuándo revisarla:** CPU o memoria saturadas de forma sostenida, necesidad de más de una instancia o de separar web y API.
- **Evolución:** ECS Fargate con ALB y una tarea por servicio (TK-095).

### Excepciones de checkov

`.checkov.yaml` omite, con su motivo, las comprobaciones que chocan con decisiones de coste o con el plan del proyecto: claves KMS propias (≈ 1 USD/mes cada una; se usan las gestionadas por AWS), réplica entre regiones (no permitida), registro de accesos y notificaciones de S3, y retenciones de registros de un año. Las excepciones puntuales van en el propio recurso con `#checkov:skip`; entre ellas, DNSSEC y el registro de consultas de la zona de Route 53 (TK-084: DNSSEC necesita una clave KMS y se deja para la evolución), y en la instancia la IP pública (sin NAT es su única salida) y la monitorización detallada (TK-085).

*Pendiente: TK-095* (resto de decisiones frente a la arquitectura prevista en el `readme.md` §2.4).

## Evolución

*Pendiente: TK-095.* Pasos recomendados cuando el proyecto sea maduro y tenga mucho tráfico, con su señal de disparo y su coste.

## Destruir el entorno

*Pendiente: TK-093.* Orden para eliminar la infraestructura sin gastar créditos y qué se conserva.
