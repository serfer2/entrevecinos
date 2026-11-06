## ADDED Requirements

### Requirement: Decisiones frente a lo previsto
«Decisiones de arquitectura» de `infra/aws/README.md` SHALL resumir en una tabla, por área (cómputo, base de datos, protección web, DNS, origen, red y secretos), lo previsto en el `readme.md`, lo elegido, el coste evitado y el riesgo aceptado, con enlace a una entrada por decisión que MUST dar como motivo el ahorro de costes mientras el proyecto no escale cuando ese sea el motivo.

#### Scenario: Por qué no hay balanceador
- **WHEN** busco por qué no hay contenedores gestionados, balanceador, RDS ni WAF
- **THEN** cada área tiene su fila y su entrada con lo previsto, lo elegido, el motivo, el coste evitado y el riesgo

### Requirement: Evolución recomendada
«Evolución» SHALL listar en orden RDS, RDS Multi-AZ, ECS Fargate con ALB, WAF, DNSSEC, origen cifrado y orígenes VPC de CloudFront, cada uno con su señal de disparo, su coste aproximado con fecha y región de referencia y sus dependencias.

#### Scenario: Hoja de ruta
- **WHEN** consulto «Evolución»
- **THEN** encuentro los siete pasos en orden con su señal y su coste

### Requirement: Resumen en el readme
`readme.md` §2.4 SHALL decir que la arquitectura difiere de la prevista para ahorrar costes mientras el proyecto no escale, con una tabla resumida y enlaces a «Decisiones de arquitectura» y «Evolución», sin repetir su detalle.

#### Scenario: Enlaces
- **WHEN** leo §2.4
- **THEN** encuentro el motivo y los enlaces a las dos secciones de la guía
