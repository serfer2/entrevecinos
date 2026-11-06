# continuous-deployment Specification

## Purpose
Despliegue continuo en producción desde GitHub Actions: cada fusión a `main` pasa las comprobaciones, publica las imágenes en ECR y las despliega por SSM con vuelta atrás visible, credenciales temporales y un solo despliegue a la vez.

## Requirements
### Requirement: Despliegue en cada fusión a main
El *workflow* `Deploy` (`.github/workflows/deploy.yml`) SHALL ejecutarse en cada `push` a `main`: pasar las comprobaciones de `ci.yml`, publicar en ECR las imágenes `prod` `linux/arm64` de `api` y `web` con la etiqueta de los 12 primeros caracteres del commit, lanzar `entrevecinos-deploy` con sus *digests* y comprobar `https://entrevecinos.org`. Si la etiqueta ya existe en ECR, MUST reutilizar su imagen. El resumen de la ejecución SHALL mostrar los *digests* y el resultado.

#### Scenario: Fusión correcta
- **WHEN** se fusiona en `main` un commit que pasa las comprobaciones
- **THEN** la instancia ejecuta las imágenes de ese commit, las migraciones se aplican y el *smoke test* pasa

#### Scenario: Comprobaciones fallidas
- **WHEN** falla un trabajo de `checks`
- **THEN** no se publica ni se despliega nada

### Requirement: Vuelta atrás visible
El trabajo `deploy` SHALL esperar al resultado del comando de SSM, mostrar la salida de `deploy.sh` y MUST fallar si el estado no es `Success`.

#### Scenario: API que no arranca
- **WHEN** se despliega un commit cuya API no supera el *healthcheck*
- **THEN** `deploy` falla y producción sigue sirviendo la versión anterior

### Requirement: Credenciales temporales
`publish` y `deploy` SHALL obtener credenciales asumiendo `entrevecinos-github-deploy` con los secretos del entorno `production`; `checks` y `smoke` MUST NOT usar ese entorno ni credenciales de AWS. El *workflow* MUST NOT recibir secretos de la aplicación.

#### Scenario: Registro de la ejecución
- **WHEN** reviso el registro de `configure-aws-credentials`
- **THEN** las credenciales proceden de asumir el rol y caducan en 1 hora

### Requirement: Un despliegue a la vez
El *workflow* SHALL usar `concurrency` `production` sin cancelación.

#### Scenario: Dos fusiones seguidas
- **WHEN** se fusionan dos *pull requests* seguidos
- **THEN** el segundo despliegue espera a que termine el primero

### Requirement: Redespliegue de un commit de main
`workflow_dispatch` SHALL aceptar un `sha` opcional y MUST rechazar commits que no estén en `main`.

#### Scenario: Commit fuera de main
- **WHEN** lanzo el *workflow* con el SHA de un commit de otra rama
- **THEN** `publish` falla sin publicar ni desplegar

