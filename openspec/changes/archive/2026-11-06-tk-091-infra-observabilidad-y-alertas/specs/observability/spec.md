## ADDED Requirements

### Requirement: Retención definida de los registros
Cada grupo de registros de producción SHALL tener una retención definida por Terraform: 14 días para `/entrevecinos/prod/app/{proxy,web,api,db,backup}`, 30 días para `/entrevecinos/prod/app/deploy` y las sesiones de SSM, y 7 días para los *flow logs* y CloudFront.

#### Scenario: Retenciones
- **WHEN** listo los grupos `/entrevecinos`
- **THEN** cada uno tiene la retención indicada y los de proxy, web y API tienen registros recientes

### Requirement: Métricas de memoria y disco
El agente de CloudWatch de la instancia SHALL publicar en `CWAgent` `mem_used_percent`, `swap_used_percent` y `disk_used_percent` de `/` y de `/srv/entrevecinos/postgres`, con la configuración en Parameter Store aplicada por State Manager, y MUST enviar el registro de las copias a `/entrevecinos/prod/app/backup`.

#### Scenario: Métricas del agente
- **WHEN** consulto el *namespace* `CWAgent`
- **THEN** hay datos de memoria, *swap* y de los dos discos de la instancia

### Requirement: Alarmas con aviso por correo
Producción SHALL tener, en `eu-north-1`, alarmas de instancia caída, CPU, créditos de CPU, memoria, disco raíz, disco de datos, copia ausente, errores de PostgreSQL, errores de la API, tasa de `5xx` de la web (registro del proxy) y rebotes y quejas de SES, que MUST avisar al tema `entrevecinos-prod-alerts` al entrar en `ALARM` y al volver a `OK`. La de instancia caída y la de copia ausente MUST tratar los datos ausentes como incumplimiento; las de errores, como cumplimiento.

#### Scenario: Aviso y vuelta a OK
- **WHEN** fuerzo una alarma a `ALARM` y vuelve a `OK`
- **THEN** recibo un correo de cada cambio

#### Scenario: Copia ausente
- **WHEN** pasan 7 horas sin la métrica `Entrevecinos/Backup` `BackupSucceeded`
- **THEN** salta la alarma «copia de la base de datos ausente»

#### Scenario: Errores de la web
- **WHEN** el proxy responde `5xx` a más del 5 % de las peticiones en 5 minutos, con al menos 10 peticiones
- **THEN** salta la alarma `entrevecinos-prod-web-5xx`

### Requirement: Panel de producción
El panel de CloudWatch `entrevecinos-prod` SHALL mostrar la instancia, la memoria y los discos, las copias, CloudFront, los rechazos `429` y los `5xx` del proxy, los errores de PostgreSQL y de la API, SES y el estado de las alarmas.

#### Scenario: Panel
- **WHEN** abro el panel `entrevecinos-prod`
- **THEN** veo esas métricas, incluidas las de CloudFront de `us-east-1`

### Requirement: Registros sin datos sensibles
Los registros de producción MUST NOT contener contraseñas, *tokens* de validación, *cookies* de sesión ni direcciones de correo de los destinatarios.

#### Scenario: Enlace de validación
- **WHEN** alguien abre `/verificar-correo?token=…`
- **THEN** los registros del proxy y de CloudFront guardan la ruta sin el *token*
