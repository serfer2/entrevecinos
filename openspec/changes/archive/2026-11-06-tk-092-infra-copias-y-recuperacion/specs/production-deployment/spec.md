## ADDED Requirements

### Requirement: Copia antes de migrar
`deploy.sh` SHALL ejecutar `backup.sh` antes de aplicar las migraciones cuando la base ya tiene esquema y hay migraciones pendientes, y si la copia falla MUST terminar con error sin migrar ni cambiar los contenedores.

#### Scenario: Migración pendiente
- **WHEN** despliego una versión con una migración nueva
- **THEN** hay una copia nueva en el bucket antes de que se aplique

#### Scenario: Sin migraciones
- **WHEN** despliego una versión sin migraciones nuevas
- **THEN** no se hace copia previa
