## 1. Infraestructura

- [x] 1.1 Grupo `/entrevecinos/prod/app/backup` y retención de 14 días en los de los contenedores (`modules/compute`)
- [x] 1.2 Salida de `entrevecinos-backup.service` a `/var/log/entrevecinos/backup.log`
- [x] 1.3 Proxy sin cadena de consulta en su registro y CloudFront con `record_fields` sin `cs-uri-query`, `cs(Cookie)` ni `cs(Referer)`
- [x] 1.4 Módulo `observability`: temas SNS y suscripciones, configuración del agente y asociación de State Manager
- [x] 1.5 Filtros de métricas, alarmas y panel; módulo en `envs/prod` con sus salidas

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: estructura, «Observabilidad y alertas» con el *runbook* de cada alarma, costes, excepción de checkov y decisión

## 3. Verificación

- [x] 3.1 `make tf-lint`, `make shellcheck` y `make tf-plan`
- [x] 3.2 `make tf-apply`, suscripciones confirmadas y despliegue (proxy y servicio de copias nuevos)
- [x] 3.3 AC1: grupos con su retención y registros recientes; proxy y CloudFront sin `?token=`
- [x] 3.4 AC3: métricas de `CWAgent` de memoria, *swap* y los dos discos; registro de copias en su grupo
- [x] 3.5 AC2: `set-alarm-state` a `ALARM` y vuelta a `OK` con correo; `web-5xx` con el contenedor `web` detenido
- [x] 3.6 AC2b: alarma de copia ausente con datos ausentes (evaluación con `describe-alarms`), sin detener las copias reales
