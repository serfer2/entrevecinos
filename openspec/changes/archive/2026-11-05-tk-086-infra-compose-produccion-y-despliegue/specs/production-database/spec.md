## MODIFIED Requirements

### Requirement: Copias cada 6 horas comprobadas
`infra/prod/backup.sh`, ejecutado cada 6 horas por `entrevecinos-backup.timer`, SHALL subir un `pg_dump` en formato personalizado al bucket de copias con SSE-S3, sin dejarlo en disco, y MUST considerarlo fallido si ocupa menos del mínimo o `pg_restore --list` no lo lee; si es correcto, MUST publicar `Entrevecinos/Backup BackupSucceeded = 1`. `deploy.sh` SHALL instalar el script y el temporizador en cada despliegue, y el script MUST localizar el contenedor `db` sin depender de los secretos del Compose.

#### Scenario: Copia correcta
- **WHEN** se ejecuta `backup.sh`
- **THEN** hay una copia nueva en `postgres/AAAA/MM/DD/` y se publica la métrica

#### Scenario: Temporizador instalado por el despliegue
- **WHEN** termina un despliegue
- **THEN** `entrevecinos-backup.timer` está activo y `backup.sh` funciona sin las variables de los secretos en su entorno
