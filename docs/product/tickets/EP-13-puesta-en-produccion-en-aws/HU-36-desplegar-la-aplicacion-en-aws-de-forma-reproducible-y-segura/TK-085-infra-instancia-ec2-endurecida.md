# TK-085 · Infraestructura: instancia EC2 endurecida para Docker Compose

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / seguridad |
| **Componente** | `infra/aws/modules/compute/` (instancia, rol IAM, *user data*), `infra/aws/envs/prod/` |
| **Historia** | HU-36 Desplegar la aplicación en AWS de forma reproducible y segura (Épica 13) |
| **Prioridad** | Alta |
| **Depende de** | TK-079, TK-080, TK-082, TK-083, TK-084 |
| **Referencias** | `readme.md` §2.5; CIS Amazon Linux 2023 Benchmark (referencia); AWS Systems Manager Session Manager y Patch Manager |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Se eligió ejecutar la web y la API con Docker Compose en una única instancia EC2 por coste, en lugar de ECS Fargate. Esto deja a nuestro cargo la seguridad del sistema operativo: parches, acceso remoto y permisos. Si alguien compromete la instancia, controla la web, la API y las credenciales del rol, así que la instancia debe tener la menor superficie posible.

**Objetivo:** una instancia sin SSH, administrada por Session Manager, con parches automáticos, IMDSv2 y un rol IAM de mínimo privilegio.

## 2. Alcance

**Incluye**
- Instancia `t4g.small` (2 vCPU, 2 GB, arm64) con la última AMI de Amazon Linux 2023 (parámetro SSM público `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64`), en una subred pública con `sg-app` e IP pública.
- Endurecimiento:
  - sin par de claves y sin puerto 22; acceso solo con Session Manager (registro de sesiones en CloudWatch Logs);
  - IMDSv2 obligatorio (`http_tokens = required`) con `http_put_response_hop_limit = 2` (los contenedores lo necesitan para obtener las credenciales del rol);
  - volumen raíz `gp3` de 20 GB cifrado y `delete_on_termination = true`;
  - volumen de datos de PostgreSQL (TK-082) adjunto con `aws_volume_attachment` (`/dev/sdf`), montado por *user data* en `/srv/entrevecinos/postgres` por UUID con `nofail`, y formateado solo si está vacío (nunca reformatear un volumen con datos);
  - *swap* de 1 GB en un fichero del volumen raíz (asumido), para absorber picos de memoria con PostgreSQL en la misma instancia;
  - `disable_api_termination = true`;
  - *user data*: `dnf upgrade`, instalación de Docker, del *plugin* Compose y del agente de CloudWatch, `dnf-automatic` solo para parches de seguridad, usuario `deploy` sin *shell* interactiva, propietario de `/opt/entrevecinos`, que **no** pertenece al grupo `docker` (`deploy.sh` lo ejecuta el agente de SSM como *root*; solo *root* accede al *daemon* de Docker, porque la configuración de los contenedores incluye los secretos, TK-086) y directorio `/opt/entrevecinos` con permisos 750.
- Patch Manager: asociación de State Manager con `AWS-RunPatchBaseline` (`Install`) semanal en ventana nocturna, con reinicio si hace falta.
- Recuperación automática: alarma de CloudWatch `StatusCheckFailed_System` → acción `recover`.
- Rol y perfil de instancia con políticas propias de mínimo privilegio:
  - `AmazonSSMManagedInstanceCore` (gestionada por AWS);
  - `s3:PutObject` y `s3:GetObject` solo en `arn:aws:s3:::entrevecinos-media-995006761619/*`;
  - `s3:PutObject` (sin `Get` ni `Delete`) solo en `arn:aws:s3:::entrevecinos-backups-995006761619/postgres/*`, y `s3:GetObject` en ese prefijo solo para `restore.sh` (TK-092; asumido: se concede, porque restaurar requiere leer; el borrado sigue denegado por la política del bucket);
  - `ses:SendEmail` solo sobre la identidad `entrevecinos.org` (TK-084) y el *configuration set* de TK-083, con condición `ses:FromAddress = no-reply@entrevecinos.org`;
  - `ssm:GetParameters` y `ssm:GetParametersByPath` solo sobre `/entrevecinos/prod/*` (secretos `SecureString` y parámetros normales; sin Secrets Manager);
  - `cloudwatch:PutMetricData` con condición `cloudwatch:namespace = Entrevecinos/Backup` para la métrica de copias (TK-082);
  - `ecr:GetAuthorizationToken` y lectura de imágenes de los dos repositorios;
  - `logs:CreateLogStream` y `logs:PutLogEvents` en los grupos de la aplicación; `cloudwatch:PutMetricData` limitado al *namespace* del agente.
- Salidas: ID de la instancia, DNS público (origen de CloudFront, TK-087) y ARN del rol.

**No incluye**
- El Compose de producción y el script de despliegue (TK-086).
- Alarmas de recursos (CPU, memoria, disco) y paneles (TK-091).

## 3. Requisitos técnicos

- `ami` con `lifecycle { ignore_changes = [ami] }`: la AMI no se cambia en cada `apply`; las actualizaciones las aplica Patch Manager. Reemplazar la instancia es un procedimiento documentado (TK-093).
- `user_data_replace_on_change = false` (asumido): cambiar el *user data* no debe recrear la instancia sin querer.
- Sin elementos `*` en `Resource` salvo donde la acción no admite recursos (`ecr:GetAuthorizationToken`). Validar las políticas con IAM Access Analyzer (`aws accessanalyzer validate-policy`).
- Docker con `live-restore` y rotación de logs locales; los logs de la aplicación van a CloudWatch con el *driver* `awslogs` (TK-086).

## 4. Criterios de aceptación

**AC1 — Sin SSH y con Session Manager (HU-36 AC3)**
- **Given** la instancia creada
- **When** intento conectar por SSH a su IP pública y, después, abro una sesión con `aws ssm start-session`
- **Then** la conexión SSH no llega (puerto cerrado) y la sesión de SSM abre y queda registrada

**AC2 — IMDSv2**
- **Given** la instancia
- **When** pido credenciales a IMDS sin token (`curl http://169.254.169.254/latest/meta-data/`)
- **Then** recibo `401`

**AC3 — Mínimo privilegio (HU-36 AC4)**
- **Given** una sesión de SSM en la instancia
- **When** intento leer un secreto, un bucket o un repositorio que no son los de la aplicación
- **Then** se deniega con `AccessDenied`, y los permitidos sí funcionan

**AC4 — Parches**
- **Given** la asociación de Patch Manager
- **When** consulto el cumplimiento de la instancia
- **Then** figura como `COMPLIANT` tras la primera ejecución

**AC5 — Recuperación**
- **Given** la alarma de *status check* del sistema
- **When** consulto su acción
- **Then** es `recover` sobre esta instancia

## 5. Plan de tareas

1. Rol, políticas y perfil de instancia; validación con Access Analyzer.
2. Instancia, IMDSv2, volumen raíz, adjunto del volumen de datos, *swap* y *user data*.
3. Session Manager con registro de sesiones.
4. Patch Manager y alarma de recuperación.
5. Comprobaciones manuales de AC1 a AC5.

## 6. Verificación

```bash
make tf-apply
aws ssm start-session --target <instance-id> --profile entrevecinos
# Dentro de la sesión:
curl -s -o /dev/null -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/   # 401
docker --version && docker compose version
aws ssm describe-instance-patch-states --instance-ids <instance-id> --profile entrevecinos
nc -zv -w 3 <ip-pública> 22   # desde el equipo: falla
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Políticas validadas sin avisos de seguridad en Access Analyzer.
- [ ] `make tf-lint` sin errores (incluido `checkov`).
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Riesgo residual frente a Fargate:** web y API comparten host y rol. Un fallo en la web daría acceso a las credenciales de la API (S3, SES, secretos). Se mitiga con contenedores sin privilegios, sistema de ficheros de solo lectura y sin socket de Docker montado (TK-086). Migrar a ECS Fargate más adelante elimina este riesgo.
- ***Hop limit* 2:** permite que cualquier contenedor obtenga las credenciales del rol, no solo la API. Alternativa: *hop limit* 1 y que solo el script de despliegue obtenga credenciales temporales para la API; añade complejidad (renovación cada pocas horas).
- **Tamaño de la instancia:** `t4g.small` (≈ 12 USD/mes) tiene 2 GB para web, API y proxy; si se queda corta, `t4g.medium`. Comprobar disponibilidad en `eu-north-1` y si cuenta como *free tier*.
- **Reinicios por parches:** pueden cortar el servicio unos minutos en la ventana nocturna; aceptable en el MVP (asumido).
