# TK-091 · Infraestructura: registros, métricas y alertas

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / operación |
| **Componente** | `infra/aws/modules/observability/`, configuración del agente de CloudWatch (TK-085), `infra/aws/envs/prod/` |
| **Historia** | HU-38 Vigilar, recuperar y operar producción (Épica 13) |
| **Prioridad** | Media |
| **Depende de** | TK-087 |
| **Referencias** | `readme.md` §2.4 («logs, métricas y alertas»); TK-083 (eventos de SES), TK-085 (agente y alarma de recuperación), TK-086 (*driver* `awslogs`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Los tickets anteriores ya envían registros a CloudWatch (contenedores, incluido PostgreSQL, sesiones de SSM, *flow logs*, copias), pero sin retención homogénea ni avisos. Sin alta disponibilidad (una sola instancia con la web, la API y PostgreSQL, mientras el proyecto no escale), cualquier fallo deja la web sin servicio, así que hay que enterarse antes que los vecinos.

**Objetivo:** grupos de registros con retención definida, métricas de memoria y disco de la instancia, y alarmas que avisen por correo.

## 2. Alcance

**Incluye**
- Grupos de registros gestionados por Terraform con retención: `/entrevecinos/prod/{proxy,web,api,db,backup}` 14 días; sesiones de SSM 30 días; *flow logs* 7 días (asumido: retenciones cortas para recortar costes).
- Configuración del agente de CloudWatch en la instancia (parámetro de SSM): `mem_used_percent`, `disk_used_percent` de `/` y de `/srv/entrevecinos/postgres` (volumen de datos), `swap_used_percent`.
- Tema SNS `entrevecinos-prod-alerts` con suscripción por correo (`alert_email`, TK-078). En `us-east-1` hace falta otro tema para las alarmas de CloudFront (sus métricas solo existen en esa región).
- Alarmas (umbrales asumidos, revisar al refinar):

  | Alarma | Condición |
  |---|---|
  | Instancia caída | `StatusCheckFailed` ≥ 1 durante 2 minutos |
  | CPU de la instancia | `CPUUtilization` > 80 % durante 15 minutos |
  | Créditos de CPU | `CPUCreditBalance` < 20 |
  | Memoria | `mem_used_percent` > 85 % durante 10 minutos |
  | Disco raíz | `disk_used_percent` de `/` > 80 % |
  | Disco de datos | `disk_used_percent` de `/srv/entrevecinos/postgres` > 75 % |
  | **Copia de la base de datos ausente** | `Entrevecinos/Backup BackupSucceeded` sin datos o < 1 durante 7 horas (datos ausentes = `breaching`), mitigación 2 de TK-082 |
  | Errores de PostgreSQL | filtro de métricas sobre `/entrevecinos/prod/db` con `FATAL` o `PANIC` > 0 en 5 minutos |
  | Errores de la web | `5xxErrorRate` de CloudFront > 5 % durante 5 minutos (`us-east-1`) |
  | Rebotes de SES | tasa de rebote > 5 % o de quejas > 0,1 % |
  | Errores de la API | filtro de métricas sobre `/entrevecinos/prod/api` con nivel `ERROR` > 10 en 5 minutos |

- Panel de CloudWatch `entrevecinos-prod` con instancia, discos, copias, CloudFront, bloqueos del WAF del plan gratuito y SES.
- Las alarmas también avisan al volver a `OK`.

**No incluye**
- Trazas distribuidas (X-Ray, OpenTelemetry) ni APM.
- Monitorización sintética (CloudWatch Synthetics; ver §8).

## 3. Requisitos técnicos

- Las alarmas tratan los datos ausentes según el caso: `breaching` en la del *status check*; `notBreaching` en las de errores.
- Los registros de la API no contienen datos personales (correo, contraseñas, tokens de validación); revisar los mensajes de *log* existentes al implementar.
- Coste: las 10 primeras alarmas y 3 paneles son gratuitos en CloudWatch; el resto, céntimos al mes (asumido).

## 4. Criterios de aceptación

**AC1 — Registros centralizados (HU-38 AC1)**
- **Given** la aplicación en marcha
- **When** consulto CloudWatch Logs
- **Then** existen los grupos de proxy, web y API con registros recientes y su retención es la definida

**AC2 — Alertas (HU-38 AC2)**
- **Given** las alarmas creadas
- **When** fuerzo una alarma (`aws cloudwatch set-alarm-state --state-value ALARM`) o detengo el contenedor `web` y provoco errores `5xx`
- **Then** recibo un correo de aviso y otro al volver a `OK`

**AC2b — Alarma de copias**
- **Given** el temporizador de copias de TK-082 detenido
- **When** pasan 7 horas sin copia
- **Then** recibo el aviso «copia de la base de datos ausente»

**AC3 — Métricas de la instancia**
- **Given** el agente configurado
- **When** consulto el *namespace* `CWAgent`
- **Then** hay datos de memoria y disco de la instancia

## 5. Plan de tareas

1. Grupos de registros y retenciones.
2. Configuración del agente.
3. Temas SNS y suscripciones.
4. Alarmas y filtro de métricas de errores de la API.
5. Panel y prueba de avisos.

## 6. Verificación

```bash
make tf-apply
aws logs describe-log-groups --log-group-name-prefix /entrevecinos --profile entrevecinos --query 'logGroups[].{n:logGroupName,r:retentionInDays}'
aws cloudwatch set-alarm-state --alarm-name entrevecinos-prod-ec2-cpu --state-value ALARM --state-reason prueba --profile entrevecinos
aws cloudwatch list-metrics --namespace CWAgent --profile entrevecinos
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Suscripciones de SNS confirmadas.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Sin monitorización externa:** si la cuenta o CloudWatch fallan, no hay aviso. Un *canary* de CloudWatch Synthetics (≈ 1-2 USD/mes con baja frecuencia) o un servicio externo gratuito de comprobación de disponibilidad cubriría ese hueco.
- **Fatiga de alertas:** umbrales asumidos; ajustar tras unas semanas en producción.
- **Alarmas en dos regiones:** CloudFront y su WAF publican métricas en `us-east-1`; es uno de los usos permitidos de esa región en el proyecto.
