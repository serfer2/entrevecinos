# TK-095 · Documentación: decisiones de la arquitectura de producción y evolución recomendada

| Campo | Valor |
|---|---|
| **Tipo** | Documentación |
| **Componente** | `infra/aws/README.md` (secciones «Decisiones de arquitectura» y «Evolución»), `readme.md` (§2.4) |
| **Historia** | HU-39 Entender las decisiones de la arquitectura de producción y mantener su documentación al día (Épica 13) |
| **Prioridad** | Media |
| **Depende de** | TK-093 |
| **Referencias** | `readme.md` §2.4 (producción prevista: contenedores gestionados, balanceador o API Gateway, PostgreSQL gestionado con alta disponibilidad, CDN + WAF); TK-078 §8 (costes), TK-082 (base de datos en la instancia), TK-084 (DNS), TK-087 (CloudFront y WAF) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El `readme.md` §2.4 preveía para producción contenedores gestionados detrás de un balanceador, PostgreSQL gestionado con alta disponibilidad y CDN con WAF. La Épica 13 despliega otra arquitectura: **una sola instancia EC2 con Docker Compose** (proxy, web, API y PostgreSQL), **sin alta disponibilidad**, detrás de CloudFront con su plan gratuito. Es una decisión de **coste, mientras el proyecto no escale**, con el límite de 40 €/mes de TK-078.

Las decisiones están repartidas por los tickets (TK-079, TK-082, TK-083, TK-084, TK-087) y TK-093 reescribe el §2.4. Falta un sitio único que explique cada diferencia frente a lo previsto, qué riesgo se acepta y cómo y cuándo evolucionar.

**Objetivo:** un registro de decisiones y una hoja de ruta de evolución en `infra/aws/README.md`, resumidos y enlazados desde el `readme.md` §2.4, que sirvan de referencia cuando el proyecto sea maduro y tenga mucho tráfico.

## 2. Alcance

**Incluye**
- **Sección «Decisiones de arquitectura»** en `infra/aws/README.md`, una entrada por decisión con: qué preveía el README, qué se ha elegido, motivo, riesgo aceptado, coste evitado y ticket de origen. Como mínimo:

  | Área | Previsto en el README | Elegido (mientras el proyecto no escale) | Coste evitado (aprox.) | Riesgo aceptado |
  |---|---|---|---|---|
  | Cómputo | Contenedores gestionados detrás de un balanceador o API Gateway | Una EC2 `t4g.small` con Docker Compose, sin balanceador (TK-085, TK-086) | ≈ 30-40 USD/mes (ALB + Fargate) | Sin alta disponibilidad; web, API y base en el mismo host; parches del SO a cargo del proyecto; despliegues con corte de segundos |
  | Base de datos | PostgreSQL gestionado con alta disponibilidad, copias y PITR | PostgreSQL 16 en la instancia, volumen EBS propio y copias cada 6 h (TK-082) | ≈ 15 USD/mes (RDS) | RPO de 6 h, sin conmutación por error, mantenimiento propio, base accesible si se compromete la instancia |
  | Protección web | CDN + WAF | Plan gratuito de CloudFront con su WAF (TK-087) | ≈ 6-10 USD/mes | Menos reglas y configuración que una Web ACL propia |
  | DNS | DNS (sin detallar) | Route 53 gestionado por Terraform, dominio registrado en Dinahosting, sin DNSSEC (TK-084) | ≈ 1 USD/mes (clave KMS de DNSSEC) | Zona sin firmar |
  | Origen | — | CloudFront → instancia por HTTP con cabecera secreta y *prefix list* (TK-079, TK-087) | — | Tramo CloudFront-origen sin cifrar |
  | Red | Red privada para la base de datos | Una subred pública, sin NAT; la base solo en la red interna de Compose (TK-079) | ≈ 35 USD/mes (NAT) | IP pública en la instancia (solo admite tráfico de CloudFront) |
  | Secretos | Gestor de secretos | Parameter Store `SecureString`, solo por entorno (TK-083, TK-086) | ≈ 1,5 USD/mes | Sin rotación gestionada; secretos visibles para *root* con `docker inspect` |

- **Sección «Evolución»** en `infra/aws/README.md`: pasos recomendados **cuando el proyecto sea maduro y tenga mucho tráfico**, en orden, cada uno con su señal de disparo, coste añadido aproximado, dependencias y ticket o procedimiento de referencia:

  | Orden | Paso | Señal para darlo (asumido) | Coste añadido (aprox.) |
  |---|---|---|---|
  | 1 | **RDS PostgreSQL** (`pg_dump` / `pg_restore`, nuevo `DATABASE_URL`; *runbook* de TK-093) | Datos que no se pueden perder 6 h, memoria de la instancia saturada por PostgreSQL o necesidad de PITR | +15 USD/mes |
  | 2 | **RDS Multi-AZ** (`multi_az = true`) | Requisito de disponibilidad de la base (p. ej. ≥ 99,9 %) o caídas de zona que afecten a usuarios | +15 USD/mes |
  | 3 | **ECS Fargate + ALB** (tareas de web y API, despliegues sin corte, autoescalado) | CPU o memoria sostenidas > 70 % incluso en `t4g.medium`, necesidad de más de una réplica o de despliegues sin corte | +30-40 USD/mes |
  | 4 | **WAF propio** (Web ACL con reglas gestionadas y límites a medida) | Superar el volumen del plan gratuito de CloudFront, ataques que el plan no frena o necesidad de reglas propias | +6-10 USD/mes |
  | 5 | **DNSSEC en Route 53** (clave KMS en `us-east-1` y `DS` en Dinahosting) | En cuanto la infraestructura esté estable; no depende del tráfico | ≈ +1 USD/mes |
  | 6 | **Origen cifrado** (`origin.entrevecinos.org` con Let's Encrypt por DNS-01 en Route 53, origen `https-only`; o certificado de ACM en el ALB del paso 3) | Antes de manejar datos más sensibles o al salir del MVP | ≈ 0 (o incluido en el ALB) |
  | 7 | **Orígenes VPC de CloudFront** (aplicación en subredes privadas, sin IP pública, sin cabecera secreta) | Junto con el paso 3, cuando la aplicación pase a subredes privadas | NAT ≈ +35 USD/mes o endpoints de interfaz |

  El orden es una recomendación: los pasos 5 y 6 se pueden adelantar porque son baratos; el 7 tiene sentido con el 3. Cada paso actualiza su entrada en «Decisiones de arquitectura» (regla de TK-094) y, si el gasto lo exige, el límite de TK-078.
- **`readme.md` §2.4:** párrafo y tabla resumida (área, previsto, elegido, evolución) que dice expresamente que la arquitectura difiere de la prevista **para ahorrar costes mientras el proyecto no escale**, con enlace a las dos secciones de `infra/aws/README.md`. Sustituye a la nota de evolución que TK-093 dejaba en el texto, para que la información no esté duplicada.

**No incluye**
- Implementar ninguno de los pasos de evolución.
- Cambios en la infraestructura desplegada.

## 3. Requisitos técnicos

- Fuente única: el detalle vive en `infra/aws/README.md`; el `readme.md` solo resume y enlaza.
- Las cifras de coste son aproximadas y se indica la fecha y la región de referencia (`eu-north-1`); se revisan al dar cada paso.
- Las señales de disparo son orientativas (asumido) y se ajustan con las métricas de TK-091.
- La entrada de la base de datos reutiliza la decisión que TK-082 registra (AC7), sin contradecirla.

## 4. Criterios de aceptación

**AC1 — Decisiones documentadas (HU-39 AC3)**
- **Given** `infra/aws/README.md`
- **When** busco por qué no hay contenedores gestionados, balanceador, RDS ni WAF propio
- **Then** cada área tiene su entrada con lo previsto, lo elegido, el motivo («ahorro de costes mientras el proyecto no escale»), el coste evitado y el riesgo aceptado

**AC2 — Evolución recomendada (HU-39 AC4)**
- **Given** la sección «Evolución»
- **When** la consulto
- **Then** encuentro, en orden, RDS (y después Multi-AZ), ECS Fargate + ALB, WAF propio, DNSSEC en Route 53, origen cifrado y orígenes VPC de CloudFront, cada uno con su señal de disparo y su coste aproximado

**AC3 — `readme.md` coherente**
- **Given** el `readme.md` §2.4
- **When** lo leo
- **Then** dice que la arquitectura difiere de la prevista para ahorrar costes mientras el proyecto no escale y enlaza a las dos secciones de `infra/aws/README.md`, sin duplicar su detalle

## 5. Plan de tareas

1. Sección «Decisiones de arquitectura» con las siete entradas.
2. Sección «Evolución» con los siete pasos.
3. Resumen y enlaces en el `readme.md` §2.4; retirar la nota duplicada de TK-093.
4. Revisión cruzada con los tickets de origen y con la tabla de costes de TK-078.

## 6. Verificación

```bash
grep -n "## Decisiones de arquitectura\|## Evolución" infra/aws/README.md
grep -n -i "mientras el proyecto no escale" readme.md infra/aws/README.md
grep -n -i "RDS\|Multi-AZ\|Fargate\|WAF propio\|DNSSEC\|origen cifrado\|orígenes VPC" infra/aws/README.md
```

Revisión en GitHub: los enlaces del `readme.md` §2.4 llevan a las secciones correctas de `infra/aws/README.md`.

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Cifras que envejecen:** los precios de AWS cambian; por eso llevan fecha y se revisan al dar cada paso.
- **Señales de disparo asumidas:** no hay datos de tráfico todavía; se fijan con las métricas reales de TK-091 tras unas semanas en producción.
- **ADR en ficheros separados:** alternativa a la sección única (`docs/architecture/decisions/ADR-xxx.md`, una por decisión). Se elige la sección en `infra/aws/README.md` por ser pocas decisiones y estar junto a la guía; si crecen, pasar a ADR.
