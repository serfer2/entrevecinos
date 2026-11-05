# aws-compute Specification

## Purpose
Instancia EC2 endurecida que ejecuta la aplicación con Docker Compose: sin SSH (Session Manager con registro), IMDSv2, rol de mínimo privilegio, volumen de datos de PostgreSQL conservado, parches automáticos y recuperación ante fallos del hardware.
## Requirements
### Requirement: Acceso solo por Session Manager
La instancia SHALL crearse sin par de claves, con `sshd` desactivado y sin el puerto 22 en su grupo de seguridad, y MUST administrarse con Session Manager, cuyas sesiones SHALL registrarse en CloudWatch Logs.

#### Scenario: SSH cerrado
- **WHEN** intento conectar por SSH a la IP pública de la instancia
- **THEN** la conexión no llega

#### Scenario: Sesión registrada
- **WHEN** abro una sesión con `aws ssm start-session`
- **THEN** la sesión se abre y su contenido queda en `/entrevecinos/prod/ssm-sessions`

### Requirement: IMDSv2 obligatorio
La instancia SHALL exigir IMDSv2 con un *hop limit* de 2 para que los contenedores obtengan las credenciales del rol.

#### Scenario: Metadatos sin token
- **WHEN** pido `http://169.254.169.254/latest/meta-data/` sin token desde la instancia
- **THEN** recibo `401`

### Requirement: Rol de mínimo privilegio
El rol de la instancia SHALL permitir solo: escribir y leer en el bucket de imágenes; escribir y leer en `postgres/` del bucket de copias, sin borrar; enviar correo desde `no-reply@entrevecinos.org` con la identidad del dominio y el *configuration set*; leer parámetros de `/entrevecinos/prod/`; descargar imágenes de los dos repositorios de ECR; publicar sus métricas y logs; y lo que necesita SSM. Ningún `Resource` SHALL ser `*` salvo en acciones que no admiten recursos, y la lectura de parámetros fuera de `/entrevecinos/prod/` (salvo los públicos de AWS) MUST denegarse expresamente, aunque la conceda una política gestionada.

#### Scenario: Recurso ajeno denegado
- **WHEN** desde la instancia intento leer un parámetro fuera de `/entrevecinos/prod/` o borrar una copia
- **THEN** recibo `AccessDenied`, y las operaciones permitidas funcionan

### Requirement: Volumen de datos conservado
El volumen de PostgreSQL SHALL adjuntarse a la instancia y montarse por UUID en `/srv/entrevecinos/postgres`, y MUST formatearse solo si no contiene un sistema de ficheros.

#### Scenario: Volumen montado
- **WHEN** consulto `findmnt /srv/entrevecinos/postgres` en la instancia
- **THEN** aparece montado desde el volumen `entrevecinos-prod-postgres`

### Requirement: Parches y recuperación
La instancia SHALL parchearse cada semana con Patch Manager y aplicar a diario los parches de seguridad con `dnf-automatic`, y una alarma de *status check* del sistema SHALL recuperarla automáticamente.

#### Scenario: Cumplimiento
- **WHEN** consulto el estado de parches de la instancia tras la primera ejecución
- **THEN** figura como `COMPLIANT`

#### Scenario: Recuperación
- **WHEN** consulto la alarma `StatusCheckFailed_System` de la instancia
- **THEN** su acción es `recover`
