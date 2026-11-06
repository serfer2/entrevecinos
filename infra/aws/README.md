# Producción en AWS

Guía de operación de producción de EntreVecinos y registro de sus decisiones de arquitectura. La infraestructura se define con Terraform en este directorio y se despliega en el proyecto de AWS `995006761619`, región `eu-north-1`. Todo cambio en `infra/aws/`, `infra/prod/`, `infra/docker-compose.prod.yml` o `.github/workflows/` debe actualizar esta guía en el mismo cambio (ver `AGENTS.md`, §Convenciones).

> **Estado:** en construcción. La Épica 13 (`docs/product/tickets/EP-13-puesta-en-produccion-en-aws/`) completa cada sección con el ticket indicado. Ya están escritos el límite de gasto y la base de Terraform (TK-078), la red (TK-079), el registro de imágenes y el bucket de fotografías (TK-080), PostgreSQL con sus copias (TK-082), SES con los secretos (TK-083), el DNS con el certificado (TK-084), la instancia (TK-085), el despliegue (TK-086) y CloudFront (TK-087).

## Estructura

```
infra/aws/
├── bootstrap/          bucket del estado de Terraform (estado local; se aplica una vez)
├── envs/prod/          composición de producción: backend S3, proveedores, variables y salidas
│   └── prod.tfvars.example   copia a prod.tfvars (no se versiona)
├── modules/
│   ├── private-bucket/ bucket S3 privado con los valores seguros comunes
│   ├── budget/         presupuesto mensual con avisos (TK-078)
│   ├── compute/        instancia EC2 endurecida, su rol, Session Manager y Patch Manager (TK-085);
│   │                   documento de despliegue, logs de los contenedores y cabecera de origen (TK-086)
│   ├── observability/  agente de CloudWatch, alarmas con aviso por correo, filtros y panel (TK-091)
│   ├── network/        VPC, subred pública, grupo de seguridad y flow logs (TK-079)
│   ├── storage/        repositorios ECR y bucket de imágenes (TK-080)
│   ├── database/       volumen de PostgreSQL, snapshots, bucket de copias y contraseñas (TK-082)
│   ├── domain/         zona de Route 53, políticas de correo y certificado HTTPS (TK-084)
│   ├── edge/           CloudFront, redirección de www, registros de acceso y alias (TK-087)
│   ├── ci/             usuario y rol de despliegue de GitHub Actions (TK-088)
│   └── mail/           SES (configuration set, dominio con DKIM y MAIL FROM) y secreto de los JWT (TK-083, TK-084)
├── .tflint.hcl         reglas de tflint
└── .checkov.yaml       comprobaciones de checkov omitidas, con su motivo
infra/docker-compose.prod.yml   Compose de producción: proxy, web, api y db (TK-086)
.github/workflows/ci.yml        comprobaciones de cada pull request (TK-089)
.github/workflows/deploy.yml    despliegue continuo en cada fusión a main (TK-090)
.github/dependabot.yml          actualizaciones semanales de dependencias (TK-089)
infra/prod/             ficheros que se copian a la instancia (TK-082, TK-086)
├── deploy.sh           despliegue: secretos, migraciones, salud y vuelta atrás
├── proxy/              nginx: exige la cabecera de origen de CloudFront
├── initdb/10-roles.sh  roles de PostgreSQL
├── backup.sh           copia de PostgreSQL a S3
└── systemd/            servicio y temporizador de las copias (registro en /var/log/entrevecinos/backup.log)
```

Versiones fijadas: Terraform 1.16.7 (`>= 1.11` en el código), proveedor `hashicorp/aws` `~> 6.70.0` y `hashicorp/random` `~> 3.9`, con `.terraform.lock.hcl` versionado para Linux y macOS (amd64 y arm64). Todo se ejecuta en contenedores con `make`:

| Comando | Qué hace |
|---|---|
| `make tf-bootstrap` | Crea el bucket del estado (una sola vez) |
| `make tf-init` | Inicializa `envs/prod` con el estado en S3 |
| `make tf-plan` / `make tf-apply` | Muestra o aplica los cambios con `prod.tfvars` (`apply` pide confirmación) |
| `make tf-output` | Muestra las salidas |
| `make tf-lint` | `terraform fmt` y `validate`, tflint y checkov; no necesita credenciales |

Las credenciales temporales de `aws login` se pasan al contenedor por entorno (`aws configure export-credentials`), sin escribirlas en disco. Recursos de CloudFront que AWS gestiona desde `us-east-1` (certificado, distribución y registros de acceso) usan el proveedor `aws.us_east_1`; el resto, `eu-north-1`. Todos llevan las etiquetas `Project = entrevecinos`, `Environment = prod` y `ManagedBy = terraform`.

## Puesta en marcha

Requisitos: Docker, AWS CLI v2 y una sesión del proyecto (`aws login --profile entrevecinos`; caduca y hay que repetirla).

1. **Límite de gasto (manual, antes que nada).** El propietario del proyecto fija **40 € al mes** en AWS Settings > Billing > *Spend limit*. Si el panel solo admite USD, se usa el equivalente redondeado hacia abajo y se anota en «Costes». Al alcanzarlo, AWS pausa el proyecto (las operaciones fallan con `AccessDenied` y la web puede caer).
2. **Estado de Terraform:** `make tf-bootstrap` crea `entrevecinos-tfstate-995006761619` (privado, cifrado, versionado). Su estado queda en `infra/aws/bootstrap/terraform.tfstate`, fuera del repositorio: consérvalo.
3. **Variables:** `cp infra/aws/envs/prod/prod.tfvars.example infra/aws/envs/prod/prod.tfvars` y ajusta el correo de avisos, el importe del presupuesto y los destinatarios de prueba de SES.
4. **Infraestructura:** `make tf-init`, `make tf-plan` y `make tf-apply`. Un segundo `make tf-plan` no debe mostrar cambios.
5. **Pasos manuales tras el `apply`:**
   - cada destinatario de `ses_test_recipients` recibe un correo de AWS y debe pulsar el enlace de verificación;
   - los avisos de AWS Budgets llegan directamente al correo configurado (no necesitan confirmación);
   - **correo «AWS Notification - Subscription Confirmation»** (tema `entrevecinos-prod-alerts`): pulsa *Confirm subscription* o no llegará ninguna alarma (TK-091);
   - **delegación del dominio** en Dinahosting (ver «DNS»), y después `wait_for_certificate_validation = true` en `prod.tfvars` y otro `make tf-apply`.
6. **Salida del *sandbox* de SES**, cuando `https://entrevecinos.org` ya responda (TK-087):

   ```bash
   aws sesv2 put-account-details --profile entrevecinos \
     --mail-type TRANSACTIONAL --website-url https://entrevecinos.org \
     --contact-language EN --additional-contact-email-addresses <correo-de-contacto> \
     --use-case-description "Transactional email for EntreVecinos, a private classifieds board for neighbourhood communities in Spain: account verification links sent once at sign-up (and on request). No marketing or bulk email. Recipients are users who just registered on https://entrevecinos.org. Bounces and complaints are tracked with an SES configuration set and the account-level suppression list; DKIM, SPF (custom MAIL FROM) and DMARC are configured for entrevecinos.org."
   aws sesv2 get-account --profile entrevecinos --query '{prod:ProductionAccessEnabled,review:Details.ReviewDetails}'
   ```

   `--contact-language` solo admite `EN` o `JA`, y la descripción va en inglés. Mientras AWS no la apruebe, SES solo envía a direcciones verificadas y como máximo 200 correos al día. Solicitada el 2026-11-06 (TK-087): revisión `GRANTED`.

7. **Primer despliegue** de la aplicación: ver «Despliegue». El mismo `make tf-apply` crea CloudFront y los alias de la web (ver «Web pública»), sin pasos en consola.
8. **Acceso de GitHub Actions** (manual en GitHub): entorno `production`, clave del usuario de CI y variables; ver «Acceso de GitHub Actions».

## Despliegue

La instancia ejecuta `infra/docker-compose.prod.yml` con cuatro servicios: `proxy` (nginx, único puerto publicado, el 80), `web`, `api` y `db`. Las imágenes de la web y la API van por *digest* desde ECR; las de nginx y PostgreSQL, fijadas por versión desde Docker Hub.

| Red | Servicios | Salida a Internet |
|---|---|---|
| `edge` | `proxy`, `web` | sí (solo el puerto 80 publicado) |
| `internal` | `web`, `api` | no |
| `data` | `api`, `db` | no |
| `egress` | `api` | sí (S3, SES e IMDS) |

- **Proxy de origen:** responde `403` a toda petición sin la cabecera `X-Origin-Verify` con el valor de `/entrevecinos/prod/origin-verify` (la añade CloudFront, TK-087) y la quita antes de reenviar a la web. Identifica al visitante por el último valor de `X-Forwarded-For` (lo añade CloudFront; el visitante no puede falsearlo) y limita por IP con `limit_req`: 4 `POST` por minuto con ráfaga de 10 a `/iniciar-sesion` y `/registro` (≈ 20 en 5 minutos) y 5 peticiones por segundo con ráfaga de 100 en general, con `429`. Su registro de accesos lleva la IP del visitante. nginx lee la plantilla solo al arrancar: `deploy.sh` pone su huella en la etiqueta `org.entrevecinos.proxy-config`, así que cambiarla recrea el proxy en el siguiente despliegue.
- **Contenedores endurecidos:** `proxy`, `web` y `api` sin *root*, con el sistema de ficheros de solo lectura (`tmpfs` donde hace falta), sin capacidades, con `no-new-privileges`, límites de memoria, CPU y procesos, y sin el socket de Docker. `db` mantiene solo las capacidades que usa la imagen oficial.
- **Logs** con el *driver* `awslogs` en `/entrevecinos/prod/app/{proxy,web,api,db}` (14 días), y la salida de cada despliegue en `/entrevecinos/prod/app/deploy` (30 días). El proxy registra la ruta sin la cadena de consulta (el enlace de validación del correo lleva el *token* en `?token=`).

### Cómo se despliega

El documento de SSM `entrevecinos-deploy` lleva dentro el Compose y `infra/prod/` (los incrusta Terraform), los escribe en `/opt/entrevecinos` y ejecuta `deploy.sh <digest de api> <digest de web>` como *root*. **Si cambias el Compose o algo de `infra/prod/`, `make tf-apply` antes de desplegar.** `deploy.sh`:

1. configura `amazon-ecr-credential-helper` (Docker pide el token de ECR con el rol; no queda ninguno en disco);
2. lee los secretos de Parameter Store y los exporta solo al entorno de su proceso;
3. descarga las imágenes, arranca `db` y crea o actualiza los roles (también aplica las contraseñas rotadas);
4. aplica las migraciones como `entrevecinos_owner` (`alembic upgrade head`);
5. arranca el resto, espera a que todo esté *healthy* y comprueba la web a través del proxy con la cabecera;
6. si falla, vuelve a los *digests* de `/opt/entrevecinos/current-digests` (sin deshacer migraciones) y termina con error;
7. guarda los *digests*, instala el temporizador de copias y borra las imágenes sin uso.

Las migraciones deben ser compatibles con la versión anterior de la API (*expand/contract*): la vuelta atrás no las deshace.

### Despliegue manual

Lo habitual es el despliegue continuo (ver «Despliegue continuo»). Para desplegar desde el equipo (p. ej., si GitHub Actions no está disponible): La instancia es `arm64`; en un equipo `amd64` hace falta la emulación de QEMU (en Ubuntu, `sudo apt-get install qemu-user-static`; comprobar con `docker buildx inspect --bootstrap`, que debe listar `linux/arm64`).

```bash
registry=995006761619.dkr.ecr.eu-north-1.amazonaws.com
tag=$(git rev-parse --short=12 HEAD)          # los tags de ECR son inmutables
aws ecr get-login-password --profile entrevecinos --region eu-north-1 |
  docker login --username AWS --password-stdin "$registry"
# Imágenes base desde la réplica oficial de ECR Public: sin el límite de descargas de Docker Hub.
bases=(--build-context python:3.12-slim=docker-image://public.ecr.aws/docker/library/python:3.12-slim
       --build-context node:22-alpine=docker-image://public.ecr.aws/docker/library/node:22-alpine)
docker buildx build --platform linux/arm64 --target prod --provenance=false "${bases[@]}" \
  -t "$registry/entrevecinos/api:$tag" --push apps/api
docker buildx build --platform linux/arm64 --target prod --provenance=false "${bases[@]}" \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://api:8000/v1 \
  -t "$registry/entrevecinos/web:$tag" --push apps/web
digest() { aws ecr describe-images --profile entrevecinos --region eu-north-1 \
  --repository-name "entrevecinos/$1" --image-ids imageTag="$tag" \
  --query 'imageDetails[0].imageDigest' --output text; }

aws ssm send-command --profile entrevecinos --region eu-north-1 \
  --document-name entrevecinos-deploy \
  --targets Key=InstanceIds,Values="$(make -s tf-output | sed -n 's/^instance_id = "\(.*\)"/\1/p')" \
  --parameters ApiDigest="$(digest api)",WebDigest="$(digest web)" \
  --cloud-watch-output-config CloudWatchOutputEnabled=true,CloudWatchLogGroupName=/entrevecinos/prod/app/deploy \
  --query Command.CommandId --output text
aws ssm list-command-invocations --profile entrevecinos --region eu-north-1 --details \
  --command-id <id> --query 'CommandInvocations[0].{estado:Status,salida:CommandPlugins[0].Output}'
```

`docker login` deja el token de ECR (válido 12 horas) en `~/.docker/config.json` del equipo; `docker logout "$registry"` lo borra.

### Acceso de GitHub Actions (TK-088)

La política de control de servicios del proyecto deniega los proveedores OIDC (`iam:CreateOpenIDConnectProvider`), así que GitHub Actions entra con la clave de acceso de un usuario IAM, `entrevecinos-github-actions`, **cuyo único permiso es asumir el rol** `entrevecinos-github-deploy` con el `ExternalId` `entrevecinos-github-actions` (`modules/ci`). Cada ejecución obtiene credenciales temporales del rol (1 hora como máximo).

| Permiso del rol | Recursos |
|---|---|
| `ecr:GetAuthorizationToken` | `*` (no admite recursos concretos) |
| Subir imágenes (`BatchCheckLayerAvailability`, `InitiateLayerUpload`, `UploadLayerPart`, `CompleteLayerUpload`, `PutImage`, `BatchGetImage`) | `entrevecinos/api` y `entrevecinos/web` |
| `ssm:SendCommand` | documento `entrevecinos-deploy` e instancia de producción (con `--instance-ids`) |
| `ssm:GetCommandInvocation`, `ssm:ListCommandInvocations` | `*` (no admiten recursos concretos; solo leen resultados) |

No puede borrar imágenes, leer Parameter Store ni ejecutar otros documentos.

**Puesta en marcha (una vez, tras `make tf-apply`)**, en GitHub, *Settings → Environments*:

1. Entorno `production` con *Deployment branches and tags* → *Selected branches and tags* → `main`. Otras ramas y los *forks* no reciben sus secretos. Opcional: *Required reviewers*.
2. Variables del entorno (no secretos): `AWS_REGION` = `eu-north-1`, `AWS_DEPLOY_ROLE_ARN` (salida `github_deploy_role_arn`), `AWS_DEPLOY_ROLE_EXTERNAL_ID` (salida `github_deploy_external_id`) y `DEPLOY_INSTANCE_ID` (salida `instance_id`).
3. Secretos del entorno `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` con una clave nueva del usuario. Con la CLI de GitHub (`gh auth login`), sin mostrarla ni escribirla en disco:

   ```bash
   aws iam create-access-key --user-name entrevecinos-github-actions --profile entrevecinos \
     --query 'AccessKey.[AccessKeyId,SecretAccessKey]' --output text |
     { read -r id secret
       printf %s "$id" | gh secret set AWS_ACCESS_KEY_ID --env production --repo serfer2/entrevecinos
       printf %s "$secret" | gh secret set AWS_SECRET_ACCESS_KEY --env production --repo serfer2/entrevecinos; }
   ```

   Sin `gh`, la misma orden sin la tubería muestra la clave una sola vez para pegarla en la web; no la guardes en ningún otro sitio. **Nunca** como secreto del repositorio ni en Terraform (`aws_iam_access_key` la dejaría en el estado).

Uso en un *workflow* (TK-090), en un *job* con `environment: production`:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-region: ${{ vars.AWS_REGION }}
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
    role-external-id: ${{ vars.AWS_DEPLOY_ROLE_EXTERNAL_ID }}
    role-duration-seconds: 3600
    role-skip-session-tagging: true   # el usuario no tiene sts:TagSession
```

`deploy.yml` lo usa en los trabajos `publish` y `deploy`.

**Rotación cada 90 días** (como mucho dos claves a la vez): crear una nueva y actualizar los secretos con la orden anterior, comprobar que un despliegue funciona y borrar la antigua (`aws iam list-access-keys` y `aws iam delete-access-key --access-key-id <antigua>`). **Si se filtra:** `aws iam update-access-key --user-name entrevecinos-github-actions --access-key-id <id> --status Inactive` y crear otra.

### Despliegue continuo (TK-090)

Cada fusión en `main` llega sola a producción con `.github/workflows/deploy.yml` (*workflow* `Deploy`):

| Trabajo | Qué hace |
|---|---|
| `checks` | Reutiliza `ci.yml` (las comprobaciones de los *pull requests*); si falla, no se publica nada |
| `publish` | Entorno `production`. Asume `entrevecinos-github-deploy`, construye `api` y `web` (`prod`, `linux/arm64`, *runner* arm64) y las sube a ECR con la etiqueta de los 12 primeros caracteres del commit. Si la etiqueta ya existe (ECR es inmutable), reutiliza la imagen. Resumen con los *digests* |
| `deploy` | Entorno `production`. Lanza `entrevecinos-deploy` con los *digests*, espera el resultado (hasta 20 min), muestra la salida de `deploy.sh` y falla si no es `Success`; si `deploy.sh` volvió atrás, producción sigue con la versión anterior |
| `smoke` | `https://entrevecinos.org/` (`200`/`307`/`308`) y `/iniciar-sesion` (`200` con `Strict-Transport-Security`), con reintentos durante 2 minutos |

- **Un despliegue cada vez:** `concurrency: production` sin cancelación. Una fusión que llega durante un despliegue espera; si llegan varias, GitHub deja pendiente solo la más reciente (que incluye las anteriores).
- **Volver a desplegar:** *Actions → Deploy → Run workflow* sobre `main`. Con el campo `sha`, despliega un commit anterior **de `main`** (los demás se rechazan) sin repetir las comprobaciones; si sus imágenes ya están en ECR, se reutilizan. Así se vuelve a una versión anterior a mano.
- **Seguimiento:** el resumen de cada ejecución muestra las imágenes y el resultado; la salida completa de `deploy.sh` está en el registro de `deploy` y en `/entrevecinos/prod/app/deploy`.
- **Fallo de `smoke`:** no vuelve atrás (la instancia ya comprobó salud y origen); revisar CloudFront y DNS.
- **Cambios de Terraform** (incluido el Compose o `infra/prod/`, que viajan en el documento de SSM): `make tf-apply` a mano **antes** de fusionar; el *workflow* nunca aplica infraestructura.

## Integración continua

`.github/workflows/ci.yml` (*workflow* `CI`) se ejecuta en cada *pull request* y como `workflow_call`: en `main` lo ejecuta el despliegue (`deploy.yml`, TK-090), una sola vez. Cinco trabajos en paralelo, con las mismas órdenes que en local:

| Trabajo | Qué hace | Local |
|---|---|---|
| `api` | `ruff check`, `ruff format --check` y `pytest` (con PostgreSQL de Compose; `.env` copiado de `.env.example`) | `make ci-api` |
| `web` | `lint`, `typecheck` y `test` sobre la imagen `dev` (sin montar el código) | `make ci-web` |
| `infra` | `terraform fmt` y `validate`, tflint y checkov; `shellcheck` de `infra/prod` | `make tf-lint`, `make shellcheck` |
| `images` | etapas `prod` de `api` y `web` para `linux/arm64` en *runners* arm64 nativos, con caché de GitHub Actions; no publica | — |
| `docs-infra` | solo en *pull requests*: falla si cambian `infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml` o `.github/workflows/**` sin `infra/aws/README.md`, salvo con la etiqueta `sin-cambios-en-doc-infra` | — |

- **Seguridad:** `permissions: contents: read`, acciones fijadas por SHA (versión en comentario; Dependabot las actualiza), `persist-credentials: false`, sin secretos ni acceso a AWS. Solo el *token* automático de solo lectura, para que tflint descargue su *plugin*. En un *pull request*, una ejecución nueva cancela la anterior; dentro del despliegue, nunca.
- **Dependabot** (`.github/dependabot.yml`): `github-actions`, `uv`, `npm`, `docker`, `docker-compose` y `terraform`, cada semana.
- **Coste:** 0; el repositorio es público (minutos ilimitados, también en `ubuntu-24.04-arm`).

**Configuración de GitHub (manual, una vez):**

1. **Etiqueta:** *Issues → Labels → New label* `sin-cambios-en-doc-infra` («El cambio de infraestructura no afecta a la guía»).
2. **Protección de `main`:** *Settings → Rules → Rulesets → New branch ruleset*: nombre `main`, *Enforcement status* `Active`, *Target branches* → *Include default branch*, y activa:
   - *Restrict deletions* y *Block force pushes*;
   - *Require a pull request before merging* con *Required approvals* `1` (con un solo mantenedor, añade tu rol a *Bypass list* para poder fusionar tus propios *pull requests*, o deja `0`);
   - *Require status checks to pass* con `api`, `web`, `infra`, `images (api)`, `images (web)` y `docs-infra` (aparecen tras la primera ejecución; los de la matriz llevan el servicio entre paréntesis).

## Web pública

`https://entrevecinos.org` sirve la web con CloudFront (`modules/edge`). CloudFront termina el HTTPS (certificado de TK-084, TLS 1.2 mínimo, HTTP/2 y HTTP/3, IPv4 e IPv6) y reenvía por HTTP al puerto 80 de la instancia, con la cabecera `X-Origin-Verify` que exige el proxy (TK-086). El grupo de seguridad solo admite el rango de CloudFront (TK-079).

| Ruta | Caché | Política de petición al origen |
|---|---|---|
| `/_next/static/*` | `Managed-CachingOptimized` (nombres con *hash*) | ninguna |
| resto (páginas, RSC, Server Actions) | `Managed-CachingDisabled` | `Managed-AllViewer`: `Host`, cookies, *query* y cabeceras del visitante |

- **Redirecciones:** `http://` → `https://` (CloudFront) y `www.entrevecinos.org/<ruta>?<query>` → `301` a `https://entrevecinos.org/<ruta>?<query>` (CloudFront Function `entrevecinos-www-redirect`).
- **Cabeceras de seguridad:** las pone Next.js (CSP con *nonce*, HSTS…); CloudFront no añade ni sustituye ninguna.
- **Sin WAF.** El plan de tarifa plana Free de CloudFront (WAF y DDoS sin coste) no está disponible: el proyecto está en el plan FREE de AWS y su política de control de servicios deniega `pricingplanmanager:*` (también desde la consola). No se contrata una web ACL por separado (≈ 10 USD/mes). DDoS: Shield Standard de CloudFront, gratuito.
- **Límites por IP en el proxy** (`infra/prod/proxy/default.conf.template`, ver «Despliegue»): `429` a partir de unos 20 `POST` en 5 minutos a `/iniciar-sesion` y `/registro`, o de 5 peticiones por segundo sostenidas.
- **Registros de acceso:** estándar (v2), en JSON, a `/entrevecinos/prod/cloudfront` en `us-east-1`, 7 días.

Comprobaciones:

```bash
dig +short A entrevecinos.org; dig +short AAAA entrevecinos.org; dig +short A www.entrevecinos.org
curl -sI http://entrevecinos.org/ | head -3                                  # 301 → https
curl -sI 'https://www.entrevecinos.org/iniciar-sesion?a=1' | grep -i '^location' # https://entrevecinos.org/iniciar-sesion?a=1
curl -sI https://entrevecinos.org/iniciar-sesion | grep -i 'strict-transport\|content-security'
for i in $(seq 1 14); do curl -s -o /dev/null -w '%{http_code} ' -X POST https://entrevecinos.org/iniciar-sesion; done  # 429 desde la 12.ª
```

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
| `entrevecinos.org`, `www.entrevecinos.org` | `A` y `AAAA` alias | Distribución de CloudFront (`modules/edge`) | Web; `www` redirige a la raíz |

Los alias no tienen TTL propio y siguen a la distribución si se recrea. TTL de 300 s durante la puesta en marcha; se subirá a 3600 (`dns_ttl`) cuando esté estable.

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

## Secretos

Todos los secretos viven en SSM Parameter Store como `SecureString` (nivel estándar, gratuito, cifrados con la clave gestionada `aws/ssm`), bajo `/entrevecinos/prod/`. No se usa Secrets Manager.

| Parámetro | Contenido | Ticket |
|---|---|---|
| `/entrevecinos/prod/jwt-secret` | Clave de firma de los JWT (64 caracteres) | TK-083 |
| `/entrevecinos/prod/db/postgres-password` | Superusuario de PostgreSQL (solo administración) | TK-082 |
| `/entrevecinos/prod/db/owner-password` | `entrevecinos_owner` (migraciones y copias) | TK-082 |
| `/entrevecinos/prod/db/app-password` | `entrevecinos_app` (la API) | TK-082 |
| `/entrevecinos/prod/db/{host,port,name}` | Conexión (`String`, no secretos): `db`, `5432`, `entrevecinos` | TK-082 |
| `/entrevecinos/prod/origin-verify` | Cabecera `X-Origin-Verify` entre CloudFront y el proxy (48 caracteres) | TK-086 |

- Los valores (salvo `origin-verify`) se generan con `ephemeral "random_password"` y se escriben con argumentos de solo escritura (`value_wo`): **no quedan en el estado de Terraform**.
- No tienen rotación automática. Para rotar: sube `jwt_secret_version` o `db_password_version` en `prod.tfvars`, `make tf-apply` y vuelve a desplegar (TK-086 aplica las contraseñas nuevas a PostgreSQL y recrea los contenedores). Rotar el secreto de los JWT invalida todas las sesiones.
- Para consultar uno (solo administración): `aws ssm get-parameter --name <nombre> --with-decryption --profile entrevecinos`.

**Cómo llegan a los contenedores (TK-086): solo por entorno.** `deploy.sh` los lee con una sola llamada a Parameter Store y los exporta al entorno de su proceso; `docker compose` los interpola (`${VAR:?}`) y se los pasa a cada contenedor. No hay `.env`, ni ficheros de contraseñas, ni temporales, y el script no los imprime (sin traza ni `docker compose config`). Consecuencias:

- `docker compose` sin esas variables falla: cualquier recreación de contenedores pasa por `deploy.sh` (para operar, `docker`; ver «Operación»). Tras un reinicio de la instancia, Docker vuelve a arrancar los contenedores existentes con su configuración guardada.
- **Rotar** cualquier secreto exige volver a desplegar, que recrea los contenedores afectados (si cambian las contraseñas de PostgreSQL, también `db`).
- **Riesgo residual:** Docker guarda el entorno de cada contenedor en `/var/lib/docker/containers/` y `docker inspect` lo muestra. Solo *root* accede (el usuario `deploy` no está en el grupo `docker`).
- **Fuera de Parameter Store:** la clave de acceso del usuario de GitHub Actions vive solo en los secretos del entorno `production` de GitHub (ver «Acceso de GitHub Actions»), no en AWS ni en el estado.
- `origin-verify` se genera con `random_password` y, a diferencia del resto, **queda en el estado de Terraform**: CloudFront lo necesita como cabecera de origen, que no admite valores de solo escritura. Solo sirve para que nadie salte CloudFront. Se rota con `origin_verify_version`.

## Operación

### Instancia de aplicación (TK-085)

Una sola instancia `entrevecinos-prod-app` (`t4g.small`, arm64, Amazon Linux 2023) en `eu-north-1a`, con IP pública y el grupo de seguridad que solo admite HTTP desde CloudFront. Ejecuta Docker Compose (TK-086).

- **Acceso solo con Session Manager:** sin par de claves, sin puerto 22 y con `sshd` desactivado. Cada sesión queda registrada en `/entrevecinos/prod/ssm-sessions` (30 días); se cierra tras 20 minutos inactiva y dura como máximo 60.

  ```bash
  aws ssm start-session --profile entrevecinos --target "$(make -s tf-output | sed -n 's/^instance_id = "\(.*\)"/\1/p')"
  ```

  Necesita el [Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) en el equipo. Sin él, se ejecutan comandos con Run Command (`aws ssm send-command --document-name AWS-RunShellScript …`) o se abre la sesión desde la consola de EC2 (*Connect* → *Session Manager*).
- **Endurecimiento:** IMDSv2 obligatorio (*hop limit* 2, para que los contenedores obtengan las credenciales del rol), volumen raíz `gp3` de 20 GB cifrado, protección contra la terminación y créditos de CPU `standard` (sin cargos por exceso; si la CPU se agota, la instancia se ralentiza).
- **Primer arranque** (`modules/compute/user-data.sh.tftpl`, registro en `/var/log/cloud-init-output.log`): actualiza el sistema e instala Docker (con `live-restore`, `no-new-privileges` y logs rotados), Compose v5.6.1 (con su SHA-256 comprobado), el agente de CloudWatch (lo configura State Manager, ver «Observabilidad y alertas») y `dnf-automatic`. Crea 1 GB de *swap*, el usuario `deploy` (sin *shell* ni grupo `docker`) y `/opt/entrevecinos` (750). Solo se ejecuta al crear la instancia: Terraform ignora sus cambios y los de la AMI.
- **Volumen de datos** de TK-082 adjunto y montado por UUID en `/srv/entrevecinos/postgres` (XFS, `nofail`). Se formatea solo si no tiene sistema de ficheros, y Docker no arranca si no está montado (`RequiresMountsFor`), así que PostgreSQL nunca escribe en el volumen raíz.
- **Parches:** `dnf-automatic` aplica a diario los de seguridad, y Patch Manager (`AWS-RunPatchBaseline`, `Install`) todos los domingos a las 04:00 UTC, reiniciando si hace falta (corte de minutos). Estado: `aws ssm describe-instance-patch-states --instance-ids <id> --profile entrevecinos`.
- **Recuperación:** la alarma `entrevecinos-prod-app-recover` recupera la instancia (mismo ID, IP y volúmenes) si falla el *status check* del sistema; `entrevecinos-prod-instance-down` avisa por correo (TK-091).
- **Rol `entrevecinos-prod-app`** (mínimo privilegio, validado con IAM Access Analyzer): `AmazonSSMManagedInstanceCore` y una política propia que permite:
  - `PutObject` y `GetObject` en el bucket de imágenes, y en `postgres/` del de copias (sin borrar);
  - `ses:SendEmail` con la identidad del dominio, el *configuration set* y, mientras haya *sandbox*, los destinatarios de prueba, solo con remitente `no-reply@entrevecinos.org`;
  - leer los parámetros de `/entrevecinos/prod/`. `AmazonSSMManagedInstanceCore` concede `ssm:GetParameter(s)` sobre `*`, así que la política deniega expresamente cualquier otro parámetro de la cuenta (solo quedan además los públicos de AWS, `/aws/*`);
  - descargar imágenes de los dos repositorios de ECR;
  - escribir en los grupos de logs `/entrevecinos/prod/app/*` y de sesiones, y publicar métricas en `Entrevecinos/Backup` y `CWAgent`.
- **Reemplazar la instancia** (nueva AMI, cambio de *user data*): procedimiento en TK-093.

### Aplicación (TK-086)

El Compose exige los secretos, así que en la instancia se opera con `docker` y las etiquetas de Compose (en una sesión de Session Manager, `sudo -i`):

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker logs --tail 50 entrevecinos-api-1        # también en /entrevecinos/prod/app/api
docker restart entrevecinos-web-1               # reinicia con la misma configuración
cat /opt/entrevecinos/current-digests           # versión desplegada
```

Para cambiar imágenes, configuración o secretos, siempre un despliegue nuevo (ver «Despliegue»).

### Web pública (TK-087)

```bash
# Rechazos por límite de peticiones en el proxy (IP del visitante en el registro de accesos)
aws logs filter-log-events --profile entrevecinos --log-group-name /entrevecinos/prod/app/proxy \
  --filter-pattern '"limiting requests"' --start-time "$(date -d '-1 hour' +%s)000" --query 'events[].message'
# Registros de acceso recientes
aws logs tail /entrevecinos/prod/cloudfront --region us-east-1 --profile entrevecinos --since 10m
# Vaciar la caché de estáticos (no suele hacer falta: cambian de nombre en cada versión)
aws cloudfront create-invalidation --profile entrevecinos \
  --distribution-id "$(make -s tf-output | awk -F'"' '/^distribution_id/ {print $2}')" --paths '/_next/static/*'
```

### Base de datos y copias (TK-082)

PostgreSQL 16 corre como contenedor `db` en la instancia, con los datos en un volumen EBS propio (`entrevecinos-prod-postgres`, 10 GB, cifrado) que sobrevive a la instancia.

- **Roles** (`infra/prod/initdb/10-roles.sh`, idempotente): `postgres` (solo administración), `entrevecinos_owner` (propietario; solo migraciones) y `entrevecinos_app` (la API: `SELECT`, `INSERT`, `UPDATE`, `DELETE`; sin DDL ni `TRUNCATE`).
- **Copias con `pg_dump`** cada 6 horas (`entrevecinos-backup.timer` a las 00, 06, 12 y 18 UTC): `backup.sh` sube la copia en *streaming* a `s3://entrevecinos-backups-995006761619/postgres/AAAA/MM/DD/`, comprueba su tamaño y que `pg_restore --list` la lee, y publica la métrica `Entrevecinos/Backup BackupSucceeded`. Se conservan 30 días.
- **Snapshots** diarios del volumen a las 03:00 UTC con Data Lifecycle Manager; se conservan 7.
- **Copias protegidas:** la política del bucket deniega el borrado a todos salvo a los roles de `admin_role_arns`; la instancia solo escribe y lee.
- Copia a demanda (p. ej. antes de una migración destructiva): `sudo systemctl start entrevecinos-backup.service` en la instancia.
- `deploy.sh` instala el script y el temporizador en cada despliegue (`/opt/entrevecinos/prod/backup.sh`). El script localiza el contenedor `db` con `docker` (por sus etiquetas de Compose), así que no necesita los secretos del despliegue.

*Pendiente: TK-092 y TK-093* (restauración probada y *runbook*).

### Observabilidad y alertas (TK-091)

Módulo `modules/observability`, todo en `eu-north-1`: la política de control de servicios del proyecto deniega SNS en `us-east-1`, y una alarma solo avisa a un tema de su región, así que las métricas de CloudFront (solo en `us-east-1`) quedan en el panel y los errores de la web se miden en el registro del proxy.

**Registros** (retención corta para recortar costes):

| Grupo | Origen | Retención |
|---|---|---|
| `/entrevecinos/prod/app/{proxy,web,api,db}` | contenedores (`awslogs`) | 14 días |
| `/entrevecinos/prod/app/backup` | `/var/log/entrevecinos/backup.log` (agente de CloudWatch) | 14 días |
| `/entrevecinos/prod/app/deploy` | salida de cada despliegue | 30 días |
| `/entrevecinos/prod/ssm-sessions` | sesiones de Session Manager | 30 días |
| `/entrevecinos/prod/vpc-flow-logs` (TK-079) y `/entrevecinos/prod/cloudfront` (`us-east-1`) | *flow logs* y accesos a la web | 7 días |

Sin datos sensibles: la API solo registra el asunto de los correos y la clave de los objetos; el proxy, la ruta sin cadena de consulta; y CloudFront, los campos elegidos (`record_fields`), sin `cs-uri-query`, `cs(Cookie)` ni `cs(Referer)`.

**Métricas del agente:** la configuración está en `/entrevecinos/prod/cloudwatch-agent` y la aplica la asociación de State Manager `entrevecinos-cloudwatch-agent` (`AmazonCloudWatch-ManageAgent`), que se vuelve a crear, y a aplicar, cuando cambia. Publica en `CWAgent`, con la dimensión `InstanceId`: `mem_used_percent`, `swap_used_percent` (cada minuto) y `disk_used_percent` de `/` y `/srv/entrevecinos/postgres` (`path`, `fstype` `xfs`; cada 5 minutos).

**Filtros de métricas** (`Entrevecinos/Logs`): `DbErrors` (`PANIC`, y `FATAL` salvo los mensajes normales de un reinicio), `ApiErrors` (`ERROR:` de uvicorn y `Traceback` de `logger.exception`), `ProxyRequests` y `Proxy5xx` (todas las peticiones del proxy y las `5xx`) y `RateLimited` (`429` del proxy, solo en el panel).

**Alarmas:** avisan por correo (tema `entrevecinos-prod-alerts`) al entrar en `ALARM` y al volver a `OK`. Umbrales iniciales; ajustarlos tras unas semanas si hay ruido.

| Alarma (`entrevecinos-prod-…`) | Condición | Qué hacer |
|---|---|---|
| `instance-down` | `StatusCheckFailed` ≥ 1 durante 2 min (sin datos = alarma) | Si es del sistema, `…-app-recover` la recupera sola. Si no, *Instance screenshot* / `get-console-output` y reiniciar la instancia (`aws ec2 reboot-instances`) |
| `cpu` | `CPUUtilization` > 80 % durante 15 min | `docker stats` en la instancia; buscar picos de tráfico (`RateLimited`, CloudFront) |
| `cpu-credits` | `CPUCreditBalance` < 20 | La instancia bajará a su rendimiento base; si se repite, revisar la carga o subir de tamaño |
| `memory` | `mem_used_percent` > 85 % durante 10 min | `docker stats`; reiniciar el contenedor que crece (`docker restart`) o revisar sus límites |
| `disk-root` | `disk_used_percent` de `/` > 80 % | `docker system df` y `docker image prune -a` (deploy.sh ya borra las imágenes sin uso); `journalctl --vacuum-size=200M` |
| `disk-data` | `disk_used_percent` del volumen de datos > 75 % | Ampliar el volumen (`aws ec2 modify-volume --size`) y `xfs_growfs /srv/entrevecinos/postgres` |
| `backup-missing` | Ninguna `BackupSucceeded` en 7 h (sin datos = alarma) | `systemctl status entrevecinos-backup.service` y `/entrevecinos/prod/app/backup`; copia a demanda con `systemctl start entrevecinos-backup.service` |
| `db-errors` | `FATAL` o `PANIC` en `/entrevecinos/prod/app/db` en 5 min | Leer el registro de `db`; contraseñas rotadas sin desplegar, disco lleno o corrupción (restaurar, TK-092) |
| `api-errors` | > 10 errores en `/entrevecinos/prod/app/api` en 5 min | Leer las trazas; si empezó con un despliegue, redesplegar el commit anterior (ver «Despliegue continuo») |
| `web-5xx` | `Proxy5xx` / `ProxyRequests` > 5 % en 5 min, con 10 peticiones o más | `docker ps` (¿web caída?) y `/entrevecinos/prod/app/{proxy,web}`. No ve un proxy caído (CloudFront responde `502` sin llegar a él): mirar `5xxErrorRate` de CloudFront en el panel |
| `ses-bounces` / `ses-complaints` | `Reputation.BounceRate` > 5 % / `Reputation.ComplaintRate` > 0,1 % | Revisar los rebotes en SES; AWS revisa la cuenta (y puede pausar el envío) a partir del 5 % y del 0,1 % |

```bash
# Probar un aviso (llega un correo de ALARM y, en la siguiente evaluación, otro de OK)
aws cloudwatch set-alarm-state --profile entrevecinos --alarm-name entrevecinos-prod-cpu \
  --state-value ALARM --state-reason "Prueba de aviso"
# Alarmas activas
aws cloudwatch describe-alarms --profile entrevecinos --state-value ALARM --query 'MetricAlarms[].AlarmName'
# Métricas del agente
aws cloudwatch list-metrics --profile entrevecinos --namespace CWAgent --query 'Metrics[].[MetricName,Dimensions[?Name==`path`].Value|[0]]' --output text
```

**Panel** `entrevecinos-prod` (CloudWatch → *Dashboards*): estado de las alarmas, CPU y créditos, memoria y *swap*, discos, copias por hora, peticiones y errores de CloudFront (`us-east-1`), errores de la API, de PostgreSQL y `5xx` del proxy, rechazos `429` y SES.

Sin monitorización externa: si la cuenta de AWS o CloudWatch fallan, no llega ningún aviso (ver «Decisiones»).

## Costes

- **Límite de gasto:** 40 €/mes en AWS Settings (manual, paso 1 de la puesta en marcha). Equivalente en USD anotado: **44 USD** (fijado el 2026-11-05).
- **Presupuesto** `entrevecinos-mensual` en AWS Budgets, igual al límite (`monthly_budget_usd`, 44 USD): avisos por correo al 50 %, 75 % y 90 % del gasto real y al 100 % del previsto.
- **Estimación** de la épica completa (sin alta disponibilidad, mientras el proyecto no escale): unos 20 USD/mes. Hasta TK-085 solo se pagan céntimos (S3, ECR, CloudWatch y el volumen de datos, ≈ 1 USD/mes) y la zona de Route 53 (0,50 USD/mes más las consultas; las de alias a CloudFront no se cobran).
- **Instancia** (TK-085): `t4g.small` ≈ 12 USD/mes más el volumen raíz de 20 GB (≈ 1,6 USD/mes). Entra en la capa gratuita del plan FREE, así que se paga con los créditos. Con créditos de CPU `standard` no hay cargos por exceso.

- **Logs de la aplicación** (TK-086): unos MB al día con el tráfico del MVP, dentro de los 5 GB de ingesta gratuitos al mes; 14 días de retención (30 los despliegues).
- **Observabilidad** (TK-091): 13 alarmas con la de recuperación; `web-5xx` usa dos métricas y cuenta como dos, así que son 14 métricas de alarma (las 10 primeras gratuitas; ≈ 0,40 USD/mes el resto). Panel, filtros de métricas y tema SNS por correo, gratuitos; métricas del agente (4 series) y de los filtros, dentro de las 10 personalizadas gratuitas o céntimos.
- **CloudFront** (TK-087): pago por uso, dentro de su capa gratuita permanente (1 TB y 10 millones de peticiones al mes) con el tráfico del MVP; Shield Standard incluido. Registros de acceso en CloudWatch Logs (`us-east-1`): céntimos al mes, 7 días de retención. Sin WAF: el plan Free de CloudFront no está disponible en el plan del proyecto y no se contrata una web ACL (≈ 10 USD/mes).

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

### Despliegue por SSM con secretos solo por entorno (TK-086)

- **Qué:** un documento de SSM con la configuración incrustada ejecuta `deploy.sh` en la instancia; los secretos van de Parameter Store al entorno de los contenedores sin pasar por disco. Proxy nginx sin *root* en lugar de Caddy.
- **Por qué:** sin SSH ni claves, sin buckets ni permisos nuevos para repartir ficheros, y la versión del documento es la versión de la configuración. Caddy no arranca sin *root* con `no-new-privileges` (su binario tiene una capacidad de fichero), y como *root* incumpliría el endurecimiento.
- **Impacto:** cambiar el Compose o `infra/prod/` exige `make tf-apply` antes de desplegar; Docker conserva el entorno de los contenedores (solo *root*); un despliegue corta el servicio unos segundos.
- **Mitigaciones:** *digests* validados por el documento, vuelta atrás automática y operación sin acceso a Docker para usuarios no *root*.
- **Cuándo revisarla:** al automatizar con GitHub Actions (TK-090) o al pasar a ECS, que inyecta secretos de Parameter Store por su cuenta.
- **Evolución:** que la API y el proxy lean los secretos al arrancar con el rol, y despliegue *blue/green* detrás del proxy.

### CloudFront sin WAF y con origen HTTP (TK-087)

- **Qué:** CloudFront delante de la IP pública de la instancia, con origen HTTP y una cabecera secreta, sin WAF; los límites de peticiones por IP los pone el proxy nginx. El ticket preveía el plan de tarifa plana Free de CloudFront, que incluye WAF.
- **Por qué:** el proyecto está en el plan FREE de AWS y su política de control de servicios deniega `pricingplanmanager:*`, así que no se puede suscribir el plan Free (ni por Terraform ni por consola). Una web ACL propia costaría ≈ 10 USD/mes y un origen VPC ≈ 35 USD/mes de NAT: **coste 0 mientras el proyecto no escale**. La política de petición `AllViewer` (no `AllViewerExceptHostHeader`) conserva el `Host` del visitante, que Next.js compara con `Origin` en las Server Actions; con origen HTTP no hay certificado que deba coincidir.
- **Impacto:** sin reglas gestionadas contra patrones maliciosos ni bots; los límites se aplican en la instancia (consumen su CPU) y con `429`; el tráfico CloudFront → instancia viaja sin cifrar y la IP de la instancia es pública.
- **Mitigaciones:** grupo de seguridad limitado a CloudFront, proxy que exige `X-Origin-Verify` (`403` sin ella), límites por la IP real del visitante, Shield Standard, cookies `Secure` y HSTS, y validación de entradas en la API.
- **Cuándo revisarla:** al pasar el proyecto al plan de pago de AWS (probar de nuevo el plan Free de CloudFront: `aws_pricingplanmanager_subscription`, ya disponible en el proveedor), con ataques que los límites del proxy no frenen o con datos más sensibles.
- **Evolución:** plan Free (o Pro) de CloudFront con su WAF; origen HTTPS con `origin.entrevecinos.org` y Let's Encrypt por DNS-01; con presupuesto, origen VPC sin IP pública.

### Usuario IAM para GitHub Actions en lugar de OIDC (TK-088)

- **Qué:** GitHub Actions usa la clave de un usuario IAM que solo puede asumir el rol de despliegue, en lugar de un proveedor OIDC de GitHub.
- **Por qué:** la política de control de servicios del proyecto (plan FREE de AWS) deniega `iam:CreateOpenIDConnectProvider`. Entre las alternativas del ticket, se elige la que no da permisos a la clave: todo pasa por un rol de mínimo privilegio con sesiones de 1 hora.
- **Impacto:** hay una clave de larga duración fuera de AWS (en GitHub) que hay que rotar a mano; AWS no puede comprobar la rama ni el repositorio de origen, así que esa restricción depende del entorno `production` de GitHub.
- **Mitigaciones:** la clave solo asume el rol (con `ExternalId`), vive en un entorno limitado a `main` (los *forks* nunca la reciben), no está en Terraform ni en el repositorio, se rota cada 90 días y su uso queda en CloudTrail. Sin rol de `terraform plan` para *pull requests*: sería otra clave al alcance de cualquier rama.
- **Cuándo revisarla:** al activar las funciones avanzadas de la cuenta o pasar a un plan que admita OIDC.
- **Evolución:** proveedor OIDC de GitHub y confianza del rol con `token.actions.githubusercontent.com:sub = repo:serfer2/entrevecinos:environment:production`; borrar el usuario y su clave.

### Integración continua con objetivos de `make` y sin AWS (TK-089)

- **Qué:** GitHub Actions ejecuta los mismos objetivos de `make` que se usan en local, en contenedores, sin secretos ni credenciales de AWS; las imágenes `arm64` se construyen en *runners* arm64 nativos.
- **Por qué:** CI y local no divergen; un *pull request* (incluido uno de un *fork*) no puede tocar AWS; los *runners* arm64 son gratuitos en repositorios públicos y evitan la emulación de QEMU, mucho más lenta.
- **Impacto:** sin `terraform plan` en los *pull requests* (los cambios de infraestructura se revisan con el `plan` local); `ci-web` no monta el código, así que construye la imagen `dev` en cada ejecución.
- **Cuándo revisarla:** si el repositorio pasa a privado (minutos de pago, sobre todo arm64) o si hace falta `plan` automático.
- **Evolución:** `plan` en *pull requests* con OIDC y un rol de lectura cuando el plan de AWS lo permita (TK-088).

### Despliegue continuo por SSM desde GitHub Actions (TK-090)

- **Qué:** cada fusión en `main` pasa CI, publica las imágenes por commit y despliega con el documento de SSM de TK-086; sin aprobación manual.
- **Por qué:** sin SSH ni puertos abiertos, con el mismo `deploy.sh` (migraciones, salud y vuelta atrás) que el despliegue manual, y con credenciales de 1 hora de un rol que solo puede publicar imágenes y lanzar ese documento.
- **Impacto:** cada fusión corta el servicio unos segundos; las imágenes se construyen dos veces (comprobación y publicación, con caché); los cambios de Terraform siguen siendo manuales y deben aplicarse antes de fusionar.
- **Mitigaciones:** `main` protegida (TK-089), un despliegue cada vez, vuelta atrás automática y redespliegue de cualquier commit anterior de `main`.
- **Cuándo revisarla:** con más personas con permiso de escritura (activar *Required reviewers* en el entorno) o cuando el corte de cada despliegue moleste.
- **Evolución:** OIDC (TK-088), despliegue *blue/green* detrás del proxy y `plan`/`apply` de Terraform en CI con un rol propio.

### Alarmas por correo con CloudWatch, sin monitorización externa (TK-091)

- **Qué:** alarmas de CloudWatch sobre las métricas de EC2, del agente, de las copias y de SES, y filtros de métricas sobre los registros (también la tasa de `5xx` del proxy), con aviso por correo desde SNS; el agente se configura con State Manager. Sin *canary* ni comprobación externa. El ticket preveía la alarma sobre `5xxErrorRate` de CloudFront con un tema SNS en `us-east-1`.
- **Por qué:** sin alta disponibilidad, hay que enterarse de un fallo antes que los vecinos; con coste casi nulo (≈ 0,40 USD/mes) y sin tocar la instancia ni `deploy.sh`. La política de control de servicios deniega SNS en `us-east-1` y una alarma no avisa a temas de otra región, así que la tasa de errores sale del registro del proxy (con un mínimo de 10 peticiones, que además evita saltar por un solo error). El tema SNS no se cifra con KMS: CloudWatch no puede publicar con la clave gestionada `aws/sns`, una propia cuesta 1 USD/mes por región y los avisos solo llevan el nombre y el estado de la alarma.
- **Impacto:** si falla la cuenta, la región o CloudWatch, no hay aviso; `web-5xx` no ve un proxy caído ni los errores de CloudFront; los umbrales son iniciales; la suscripción de correo se confirma a mano.
- **Mitigaciones:** `instance-down` y `backup-missing` tratan la falta de datos como alarma; avisos también al volver a `OK`; *runbook* por alarma.
- **Cuándo revisarla:** con usuarios que dependan de la web a diario, más de una persona de guardia o ruido de alertas.
- **Evolución:** un *canary* de CloudWatch Synthetics (≈ 1-2 USD/mes) o un servicio externo gratuito de disponibilidad; avisos a un canal de chat; con el plan de pago, la alarma sobre `5xxErrorRate` de CloudFront en `us-east-1` (TK-095).

### Excepciones de checkov

`.checkov.yaml` omite, con su motivo, las comprobaciones que chocan con decisiones de coste o con el plan del proyecto: claves KMS propias (≈ 1 USD/mes cada una; se usan las gestionadas por AWS), réplica entre regiones (no permitida), registro de accesos y notificaciones de S3, y retenciones de registros de un año. Las excepciones puntuales van en el propio recurso con `#checkov:skip`; entre ellas, DNSSEC y el registro de consultas de la zona de Route 53 (TK-084: DNSSEC necesita una clave KMS y se deja para la evolución), en la instancia la IP pública (sin NAT es su única salida) y la monitorización detallada (TK-085), y en CloudFront la restricción geográfica, el origen de respaldo y la política de cabeceras de respuesta (las pone Next.js), con los registros v2 que checkov no reconoce, y la falta de WAF (TK-087), el usuario IAM con política propia de GitHub Actions (TK-088), y el tema SNS sin KMS y la configuración del agente como `String` (TK-091).

*Pendiente: TK-095* (resto de decisiones frente a la arquitectura prevista en el `readme.md` §2.4).

## Evolución

*Pendiente: TK-095.* Pasos recomendados cuando el proyecto sea maduro y tenga mucho tráfico, con su señal de disparo y su coste.

## Destruir el entorno

*Pendiente: TK-093.* Orden para eliminar la infraestructura sin gastar créditos y qué se conserva.
