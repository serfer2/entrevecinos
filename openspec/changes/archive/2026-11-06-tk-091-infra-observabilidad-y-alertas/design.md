## Context

TK-085 instaló el agente de CloudWatch sin configurar y permitió al rol publicar en `CWAgent`; TK-082 publica `Entrevecinos/Backup` `BackupSucceeded` tras cada copia; TK-083 activó las métricas de reputación de SES; TK-086 y TK-087 crearon los grupos de los contenedores (30 días) y de CloudFront (7 días). Faltan avisos, métricas del sistema y el registro de las copias, que hoy solo está en el *journal*.

## Goals / Non-Goals

**Goals:** enterarse por correo de que la web, la instancia, la base de datos o las copias fallan; retenciones cortas y definidas; registros sin datos sensibles.

**Non-Goals:** trazas, APM y monitorización sintética (sin aviso si falla la propia cuenta, ver riesgos).

## Decisions

- **Todo en `eu-north-1`, errores de la web desde el proxy.** El ticket preveía la alarma sobre `5xxErrorRate` de CloudFront (solo en `us-east-1`) con un tema SNS allí, pero la política de control de servicios del proyecto deniega SNS en `us-east-1` (comprobado al aplicar) y una alarma solo avisa a temas de su región. La alarma `web-5xx` calcula `100 * Proxy5xx / ProxyRequests` con filtros sobre el registro del proxy, solo con 10 peticiones o más en 5 minutos. El panel muestra CloudFront leyendo `us-east-1`.
- **Agente configurado por State Manager.** La configuración vive en `/entrevecinos/prod/cloudwatch-agent` (la instancia ya lee ese prefijo) y una asociación con `AmazonCloudWatch-ManageAgent` la aplica. `replace_triggered_by` sobre el parámetro recrea la asociación, y la vuelve a aplicar, cuando cambia. No se toca `deploy.sh` ni el *user data* (que solo se ejecuta al crear la instancia).
- **Dimensiones fijas en el agente.** Solo `InstanceId` (`append_dimensions`) y, en los discos, `path` y `fstype` (`drop_device`), para que las alarmas apunten a series conocidas. Los dos sistemas de ficheros son `xfs`.
- **Copia ausente con 7 periodos de 1 hora.** `Sum` de `BackupSucceeded` < 1 en 7 de 7 periodos, con datos ausentes como incumplimiento: con una copia cada 6 horas, nunca hay 7 horas seguidas sin dato salvo que falte una copia.
- **Errores por filtros de métricas** en `Entrevecinos/Logs`: `PANIC`, y `FATAL` sin los mensajes normales de un reinicio (`administrator command`, `the database system is`); en la API, las líneas `ERROR:` de uvicorn y los `Traceback` de `logger.exception` (la app no configura *logging*: Python escribe el mensaje y la traza sin nivel). También `429` del proxy, solo para el panel: sustituye a los bloqueos del WAF, que no existe (TK-087).
- **SNS sin cifrado KMS.** Las alarmas de CloudWatch no pueden publicar en un tema cifrado con la clave gestionada `aws/sns`; una clave propia cuesta 1 USD/mes por región. Los avisos solo llevan el nombre y el estado de la alarma. Excepción de checkov documentada.
- **Sin cadena de consulta en los registros.** El *token* de validación viaja en `?token=`. El proxy registra `$request_method $uri $server_protocol` en lugar de `$request`, y CloudFront usa `record_fields` sin `cs-uri-query`, `cs(Cookie)` ni `cs(Referer)` (el *referer* repetiría la URL anterior). Los mensajes de la API ya no registran destinatarios: solo el asunto del correo y la clave del objeto subido.
- **Retenciones:** 14 días los contenedores y las copias; 30 los despliegues y las sesiones (auditoría); 7 los *flow logs* y CloudFront.

## Risks / Trade-offs

- **Sin monitorización externa:** si la cuenta o CloudWatch fallan, no hay aviso. Un *canary* o un servicio externo gratuito lo cubriría (TK-095).
- **Errores que el proxy no ve:** con el proxy caído, CloudFront responde `502` sin llegar a la instancia y `web-5xx` no salta; queda el panel de CloudFront y la prueba de humo de cada despliegue. Umbrales a revisar tras unas semanas.
- **Coste:** 13 alarmas (con la de recuperación de TK-085; `web-5xx` cuenta como dos métricas) superan las 10 gratuitas: unos 0,40 USD/mes; el panel y los filtros son gratuitos.
- **Confirmación manual:** las suscripciones de correo quedan pendientes hasta confirmarlas; sin eso no llega ningún aviso.
