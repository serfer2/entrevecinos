## ADDED Requirements

### Requirement: Arquitectura real en el readme
`readme.md` §2.4 SHALL mostrar en un diagrama Mermaid la producción desplegada, en el que cada componente exista en `infra/aws/` y no aparezcan balanceador, API Gateway, RDS ni Secrets Manager; MUST explicar que PostgreSQL corre en la instancia, sin alta disponibilidad, para ahorrar costes mientras el proyecto no escale, resumir la integración y el despliegue continuos y no contener la nota «Pendiente». §2.5 MUST describir las medidas de seguridad implementadas.

#### Scenario: Diagrama y recursos
- **WHEN** comparo el diagrama de §2.4 con los recursos de Terraform
- **THEN** todos sus componentes existen y la base de datos figura como PostgreSQL en la instancia

### Requirement: Guía reproducible
`infra/aws/README.md` SHALL permitir, sin ayuda, crear el entorno, desplegar, nombrar un `platform_admin`, volver a una versión anterior, rotar secretos, actualizar PostgreSQL, reemplazar la instancia, consultar los costes y destruir el entorno, con comandos que se copian tal cual y marcadores `<…>` solo donde el valor depende del despliegue, y MUST NOT contener secretos.

#### Scenario: Tareas del runbook
- **WHEN** busco cómo nombrar un `platform_admin` o destruir el entorno
- **THEN** encuentro los pasos exactos en `infra/aws/README.md`

### Requirement: Agentes y confirmación
`AGENTS.md` SHALL indicar dónde está la infraestructura de producción y sus comandos `make tf-*`, y MUST exigir confirmación explícita antes de `make tf-apply`, `destroy`, un despliegue o cualquier orden que cambie producción.

#### Scenario: Agente que aplica Terraform
- **WHEN** un agente busca cómo aplicar la infraestructura
- **THEN** encuentra los comandos y la obligación de pedir confirmación antes
