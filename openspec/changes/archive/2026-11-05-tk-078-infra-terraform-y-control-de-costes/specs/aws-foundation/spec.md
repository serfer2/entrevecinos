## ADDED Requirements

### Requirement: Límite de gasto y avisos
El proyecto de AWS SHALL tener un límite de gasto de 40 €/mes configurado en AWS Settings antes de crear ningún recurso, y Terraform MUST crear un presupuesto mensual del mismo importe que avise por correo al 50 %, 75 % y 90 % del gasto real y al 100 % del previsto.

#### Scenario: Avisos de gasto
- **WHEN** consulto AWS Budgets tras el `apply`
- **THEN** existe `entrevecinos-mensual` con los cuatro avisos dirigidos a `alert_email`

### Requirement: Estado remoto de Terraform
El estado de producción SHALL guardarse en el bucket `entrevecinos-tfstate-<cuenta>` (privado, cifrado, versionado, solo TLS y protegido contra borrado) con bloqueo nativo (`use_lockfile`), y los recursos MUST llevar las etiquetas `Project`, `Environment` y `ManagedBy` y crearse en `eu-north-1`, salvo los declarados con el alias `us_east_1`.

#### Scenario: Plan sin cambios
- **WHEN** ejecuto `make tf-plan` tras un `make tf-apply`
- **THEN** no hay cambios y el estado está en el bucket

### Requirement: Calidad de la infraestructura en contenedores
`make tf-lint` SHALL ejecutar en contenedores, sin credenciales, `terraform fmt -check`, `terraform validate` de cada raíz, tflint y checkov, y MUST terminar sin errores; las comprobaciones de checkov omitidas MUST tener su motivo escrito.

#### Scenario: Lint limpio
- **WHEN** ejecuto `make tf-lint`
- **THEN** todas las herramientas terminan sin errores
