# TK-078 · Infraestructura: límite de gasto, base de Terraform y control de costes

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura |
| **Componente** | AWS Settings > Billing (límite de gasto, manual), `infra/aws/` (nuevo), `.gitignore` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta (primer ticket de la épica) |
| **Depende de** | — |
| **Referencias** | `readme.md` §2.4; documentación de Terraform «S3 backend» (`use_lockfile`); AWS Budgets; «Spend limits» y SCP de los proyectos de AWS (`docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`readme.md` §2.4 describe la producción en cloud solo en abstracto y la deja pendiente para la entrega 3. Antes de crear ningún recurso hay que **limitar el gasto del proyecto a 40 € al mes**, y después preparar una base de Terraform común (estructura, proveedores, estado remoto y etiquetas) y un presupuesto con avisos: el proyecto de AWS está en el plan gratuito con 100 USD de créditos (hasta 2027-04-30), así que un recurso olvidado puede agotarlos.

Datos del proyecto: cuenta `995006761619`, región `eu-north-1` (no se puede cambiar; solo se permite `us-east-1` para recursos globales como WAF de CloudFront).

**Objetivo:** que el proyecto no pueda gastar más de 40 € al mes y avise antes de llegar a ese importe, y dejar listo `infra/aws/` para que los tickets siguientes solo añadan módulos, con el estado guardado en S3 y un presupuesto que avise antes de gastar los créditos.

## 2. Alcance

**Incluye**
- **Límite de gasto del proyecto: 40 € al mes.** Es lo primero de la épica: se configura antes de crear ningún recurso, ni siquiera el bucket del estado.
  - Lo configura el **propietario del proyecto** en AWS Settings > Billing > *Spend limit* (paso manual; no se gestiona con Terraform).
  - Importe: 40 € al mes. Si el panel solo admite USD, se usa el equivalente redondeado hacia abajo con el cambio del día y se anota en `infra/aws/README.md` (44 USD, fijado el 2026-11-05).
  - Al alcanzarlo, AWS **pausa el proyecto**: los SCP del proyecto deniegan las acciones (crear o arrancar instancias, servicios, distribuciones…) y producción puede quedar sin servicio hasta el mes siguiente o hasta que el propietario suba el límite. Es la red de seguridad; los avisos de AWS Budgets están para no llegar a ella.
  - Los créditos del plan gratuito (100 USD) se consumen antes que el límite; el límite protege también cuando se agoten o al pasar al plan de pago (asumido: comprobar en AWS Settings cómo cuentan los créditos para el límite).
- Estructura de directorios:

  ```
  infra/aws/
  ├── bootstrap/            # bucket del estado (estado local, se aplica una vez)
  ├── modules/              # un módulo por área: network, storage, database, mail, compute, edge, ci, observability
  ├── envs/prod/            # composición de módulos, backend.tf, providers.tf, variables.tf, outputs.tf
  ├── .tflint.hcl
  └── README.md             # ya existe (esqueleto de TK-094); este ticket completa «Estructura», «Puesta en marcha» y «Costes»
  ```
- `bootstrap/`: bucket S3 del estado con versionado, cifrado SSE-S3, Block Public Access, política que deniega peticiones sin TLS y `prevent_destroy`.
- `envs/prod/backend.tf`: *backend* `s3` con `use_lockfile = true` (bloqueo nativo, sin tabla de DynamoDB), `encrypt = true`.
- `providers.tf`: proveedor `aws` en `eu-north-1` y alias `aws.us_east_1` **solo** para los recursos globales de CloudFront: certificado de ACM (TK-084; la zona de Route 53 es global y usa el proveedor por defecto) y, si lo requiere, el plan de tarifa plana y su WAF (TK-087); `default_tags` (`Project = entrevecinos`, `Environment = prod`, `ManagedBy = terraform`).
- Versiones fijadas: Terraform `>= 1.11` (`use_lockfile` desde 1.10; argumentos de solo escritura y recursos `ephemeral`, que usa TK-082, desde 1.11) y proveedor `hashicorp/aws ~> 6.x` con `.terraform.lock.hcl` versionado (asumido: la última versión mayor estable al implementar).
- AWS Budgets: presupuesto mensual de coste **igual al límite de gasto** (40 € en su equivalente en USD, variable `monthly_budget_usd`) con avisos por correo al 50 %, 75 % y 90 % del gasto real y al 100 % del previsto, para reaccionar antes de que el límite pause el proyecto.
- `tflint` (con el *ruleset* de AWS) y `checkov` ejecutables en contenedor (`make tf-lint`), sin instalar nada en el host.
- `.gitignore`: `.terraform/`, `*.tfstate*`, `*.tfvars` (salvo `*.tfvars.example`).

**No incluye**
- Recursos de la aplicación (tickets TK-079 en adelante).
- Ejecución de Terraform en CI (TK-089).

## 3. Requisitos técnicos

- Terraform y las herramientas se ejecutan en contenedores (`hashicorp/terraform`, `ghcr.io/terraform-linters/tflint`, `bridgecrew/checkov`) con imágenes fijadas por versión, coherente con `AGENTS.md` («no instales dependencias en el host»).
- Credenciales: perfil `entrevecinos` de `aws login`, montado en el contenedor como solo lectura (`~/.aws`) con `AWS_PROFILE=entrevecinos`. Nunca claves en variables del repositorio.
- Nombre del bucket de estado: `entrevecinos-tfstate-995006761619` (único por incluir la cuenta).
- El correo de los avisos es una variable (`alert_email`) en `prod.tfvars`, que no se versiona; se versiona `prod.tfvars.example`.
- Objetivos del `Makefile`: `tf-init`, `tf-plan`, `tf-apply`, `tf-lint` (asumido: mismo patrón que `make dev`).

## 4. Criterios de aceptación

**AC0 — Límite de gasto (HU-36 AC5)**
- **Given** el proyecto antes de crear ningún recurso de la épica
- **When** consulto AWS Settings > Billing
- **Then** hay un límite de gasto mensual de 40 € (o su equivalente en USD anotado en `infra/aws/README.md`)

**AC1 — Estado remoto con bloqueo (HU-36 AC1)**
- **Given** el *bootstrap* aplicado
- **When** ejecuto `make tf-init` y `make tf-plan` en `envs/prod`
- **Then** el estado se guarda en el bucket con versionado y cifrado, y dos `plan` simultáneos no pueden tomar el bloqueo a la vez

**AC2 — Etiquetas y región**
- **Given** cualquier recurso creado por Terraform
- **When** consulto sus etiquetas y su región
- **Then** lleva las tres etiquetas por defecto y está en `eu-north-1`, salvo los que se declaran explícitamente con el alias `us_east_1`

**AC3 — Avisos de coste (HU-36 AC5)**
- **Given** el presupuesto creado
- **When** consulto AWS Budgets
- **Then** su importe coincide con el límite de gasto y existen los avisos al 50 %, 75 % y 90 % del gasto real y al 100 % del previsto, dirigidos al correo configurado, y el correo de confirmación de la suscripción se ha aceptado

**AC4 — Calidad**
- **Given** el código de `infra/aws/`
- **When** ejecuto `make tf-lint`
- **Then** `terraform fmt -check`, `terraform validate`, `tflint` y `checkov` terminan sin errores

## 5. Plan de tareas

1. **Límite de gasto de 40 € al mes en AWS Settings > Billing** (propietario del proyecto), antes que nada.
2. Estructura de directorios, `.gitignore` y objetivos del `Makefile`.
3. `bootstrap/` y aplicación única con estado local.
4. `envs/prod` con *backend*, proveedores, versiones y etiquetas.
5. Módulo o recurso de AWS Budgets con el importe del límite.
6. Configuración de `tflint` y `checkov` y primera ejecución limpia.

## 6. Verificación

```bash
# AWS Settings > Billing: límite de gasto de 40 €/mes configurado (manual)
aws login --profile entrevecinos
make tf-init && make tf-plan          # sin errores, estado en S3
make tf-lint
aws s3api get-bucket-versioning --bucket entrevecinos-tfstate-995006761619 --profile entrevecinos
aws budgets describe-budgets --account-id 995006761619 --profile entrevecinos
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Ningún secreto ni `*.tfstate` en el repositorio.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Terraform frente a CDK u OpenTofu:** se eligió Terraform. OpenTofu es compatible y de licencia abierta (MPL); puede sustituirlo sin cambiar el código si la licencia BSL de Terraform preocupa.
- **Bloqueo nativo frente a DynamoDB:** `use_lockfile` evita una tabla extra; requiere Terraform ≥ 1.10 (la épica fija ≥ 1.11 por TK-082).
- **Coste estimado y margen:** sin alta disponibilidad y con los recortes de la épica (PostgreSQL en la instancia en vez de RDS, plan gratuito de CloudFront en vez de WAF de pago, Parameter Store en vez de Secrets Manager, una sola subred y retenciones cortas), el coste es de unos 20 USD al mes (asumido):

  | Partida | USD/mes (aprox.) |
  |---|---|
  | EC2 `t4g.small` | 12 |
  | IPv4 pública | 3,6 |
  | EBS raíz (20 GB) + datos (10 GB) + *snapshots* | 3 |
  | CloudWatch (registros, métricas, alarmas) | 1-2 |
  | S3 (imágenes y copias), ECR, SES | < 1 |
  | Route 53 (zona alojada de `entrevecinos.org`, TK-084) | 0,5 |
  | CloudFront (plan Free), Parameter Store, Budgets | 0 |

  Deja margen frente a los 40 €. Partidas que lo romperían: pasar a `t4g.medium` si falta memoria (+12), RDS (+15), WAF propio (+6-10) o NAT Gateway (+35); cualquiera de ellas es una decisión del proyecto para cuando escale.
- **Proyecto pausado al alcanzar el límite:** las operaciones empiezan a fallar con `AccessDenied` y la web puede caer. Si ocurre, revisar el gasto en AWS Billing and Cost Management y, si procede, que el propietario suba el límite en AWS Settings. Se documenta en el *runbook* de TK-093.
- **Moneda:** AWS factura en USD; el límite de 40 € depende del cambio. Revisar el equivalente cada cierto tiempo (asumido: al refinar y una vez al trimestre).
