## Context

Red, imágenes, volumen de datos, SES, DNS y parámetros ya existen (TK-078 a TK-084). El Compose de producción y `deploy.sh` llegan en TK-086; las alarmas de recursos, en TK-091.

## Goals / Non-Goals

**Goals:** instancia con la menor superficie posible, administrable sin SSH, con parches automáticos y permisos mínimos; volumen de datos montado sin riesgo de perderlo.

**Non-Goals:** contenedores de la aplicación y despliegue (TK-086); alarmas de CPU, memoria y disco (TK-091).

## Decisions

- **`t4g.small` con créditos `standard`:** entra en la capa gratuita del plan FREE; en modo `unlimited` (el de por defecto en T4g) un pico sostenido generaría cargos fuera de los créditos. Si se queda corta: `t4g.medium`.
- **`ignore_changes = [ami, user_data]`:** el *user data* solo actúa en el primer arranque; cambiarlo no debe parar ni recrear la instancia. Los cambios posteriores se aplican por SSM y las actualizaciones, con Patch Manager. Reemplazar la instancia es un procedimiento documentado (TK-093).
- **Volumen por su ID:** en instancias Nitro el dispositivo aparece como `/dev/nvme1n1`, no `/dev/sdf`; el *user data* espera a `/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_<id>` (el adjunto se crea después de la instancia), formatea en XFS solo si `blkid` no encuentra sistema de ficheros y monta por UUID con `nofail`.
- **`sshd` desactivado** además de no tener clave ni puerto 22: defensa en profundidad.
- **Compose desde GitHub** con versión y SHA-256 fijados: Amazon Linux 2023 no lo empaqueta.
- **SES:** `ses:SendEmail` sobre la identidad del dominio, el *configuration set* y, mientras haya *sandbox*, las identidades de los destinatarios de prueba (SES también autoriza contra ellas), con `ses:FromAddress = no-reply@entrevecinos.org`.
- **Parámetros:** `AmazonSSMManagedInstanceCore` permite `ssm:GetParameter(s)` sobre `*`. Una denegación explícita (`NotResource`: `/entrevecinos/prod`, `/entrevecinos/prod/*` y los públicos `arn:aws:ssm:<región>::parameter/aws/*`) limita la lectura a producción sin reescribir la política gestionada, que seguiría las actualizaciones de AWS.
- **Logs de la aplicación** en `/entrevecinos/prod/app/*` (los grupos los crea TK-086) y de las sesiones en `/entrevecinos/prod/ssm-sessions` (30 días). `logs:DescribeLogGroups` necesita `*` (Session Manager).
- **Preferencias de Session Manager** como documento `SSM-SessionManagerRunShell` gestionado por Terraform (no existía): registro en CloudWatch, sesión inactiva 20 min, máximo 60 min.
- **Patch Manager:** `AWS-RunPatchBaseline` `Install` con `RebootIfNeeded` los domingos a las 04:00 UTC (fuera de las copias y del *snapshot*); se ejecuta también al crear la asociación para dejar la instancia `COMPLIANT`.
- **Sin monitorización detallada** (checkov `CKV_AWS_126`): cuesta y las métricas de 5 minutos bastan; **IP pública** (`CKV_AWS_88`): sin NAT es la única salida, y la entrada la limita el grupo de seguridad a CloudFront.

## Risks / Trade-offs

- [Web y API comparten host y rol] → contenedores sin privilegios y sin socket de Docker (TK-086); evolución a ECS Fargate.
- [*Hop limit* 2: cualquier contenedor obtiene las credenciales del rol] → aceptado; alternativa documentada en el ticket.
- [Reinicios por parches de madrugada] → corte de minutos aceptable en el MVP.
- [Formatear un volumen con datos] → solo si `blkid` no detecta sistema de ficheros.
