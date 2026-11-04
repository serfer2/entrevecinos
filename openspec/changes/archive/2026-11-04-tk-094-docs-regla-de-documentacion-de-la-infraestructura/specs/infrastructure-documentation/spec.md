## ADDED Requirements

### Requirement: Rutas de infraestructura
El proyecto SHALL considerar rutas de infraestructura `infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml` y `.github/workflows/**`, y MUST usar esa misma lista en `openspec/config.yaml`, en `AGENTS.md` y en la plantilla de *pull request*.

#### Scenario: Lista única
- **WHEN** comparo las rutas citadas en `openspec/config.yaml`, `AGENTS.md` y `.github/pull_request_template.md`
- **THEN** son las mismas cuatro

### Requirement: Guía de producción como destino de la documentación
El repositorio SHALL contener `infra/aws/README.md` como guía de operación de producción y registro de decisiones de arquitectura, con secciones para la estructura de `infra/aws/`, la puesta en marcha, el despliegue, el DNS, los secretos, la operación (*runbook*), los costes, las decisiones de arquitectura, la evolución y la destrucción del entorno; las secciones aún no implementadas MUST indicar el ticket que las completará.

#### Scenario: Esqueleto disponible
- **WHEN** abro `infra/aws/README.md` antes de implementar el resto de la Épica 13
- **THEN** encuentro todas las secciones, cada una con el ticket que la completará

#### Scenario: Enlace desde infra
- **WHEN** abro `infra/README.md`
- **THEN** encuentro un enlace a `infra/aws/README.md`

### Requirement: Regla de OpenSpec para cambios de infraestructura
`openspec/config.yaml` SHALL describir en `context` la infraestructura de producción y las rutas de infraestructura, y sus `rules` MUST exigir que un change que toque esas rutas lo indique en Impact (`proposal`), actualice la entrada de «Decisiones de arquitectura» si cambia una decisión (`design`) e incluya en el grupo Documentación una tarea que actualice `infra/aws/README.md` (`tasks`).

#### Scenario: Change de infraestructura
- **WHEN** se generan los artefactos de un change que modifica `infra/aws/`
- **THEN** las instrucciones de `proposal`, `design` y `tasks` incluyen las reglas sobre `infra/aws/README.md`

#### Scenario: Configuración válida
- **WHEN** el CLI de OpenSpec lee `openspec/config.yaml`
- **THEN** la carga sin errores

### Requirement: Regla para agentes
`AGENTS.md` SHALL incluir en §Convenciones la viñeta «Infraestructura», que MUST indicar las rutas de infraestructura y la obligación de actualizar `infra/aws/README.md` en el mismo cambio.

#### Scenario: Viñeta presente
- **WHEN** leo §Convenciones de `AGENTS.md`
- **THEN** encuentro «Infraestructura» junto a «Contrato» y «Esquema», con las cuatro rutas y `infra/aws/README.md`

### Requirement: Recordatorio en los pull requests
`.github/pull_request_template.md` SHALL incluir la casilla «Si cambia la infraestructura, he actualizado `infra/aws/README.md`.».

#### Scenario: Pull request nuevo
- **WHEN** abro un *pull request* en GitHub
- **THEN** su descripción parte de la plantilla con esa casilla
