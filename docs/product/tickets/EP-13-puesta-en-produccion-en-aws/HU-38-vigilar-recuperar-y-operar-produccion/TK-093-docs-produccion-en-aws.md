# TK-093 · Documentación: producción en AWS y guía de operación

| Campo | Valor |
|---|---|
| **Tipo** | Documentación |
| **Componente** | `readme.md` (§2.4, §2.5), `infra/aws/README.md`, `infra/README.md`, `AGENTS.md`, `.env.example` |
| **Historia** | HU-38 Vigilar, recuperar y operar producción (Épica 13) |
| **Prioridad** | Media |
| **Depende de** | TK-090, TK-092 |
| **Referencias** | `readme.md` §2.4 («Pendiente: se completará en la entrega 3»); TK-078 a TK-092 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`readme.md` §2.4 describe la producción de forma genérica (DNS + CDN + WAF, balanceador o API Gateway, contenedores gestionados) y termina con «**Pendiente**». Tras esta épica la infraestructura es concreta y distinta en algunos puntos: no hay balanceador ni API Gateway, la API no es pública, y la web, la API y PostgreSQL corren en una sola instancia EC2 sin alta disponibilidad, **para ahorrar costes mientras el proyecto no escale**. Además faltan los procedimientos para operar producción.

**Objetivo:** que la documentación describa la infraestructura desplegada y que cualquier persona del proyecto pueda crearla, desplegarla, operarla y destruirla siguiendo la guía.

## 2. Alcance

**Incluye**
- `readme.md` §2.4:
  - diagrama Mermaid de producción real: `entrevecinos.org` (registrado en Dinahosting, DNS en Route 53) → CloudFront (sin WAF; límite de peticiones en el proxy, TK-087) → instancia EC2 (proxy, web, API, PostgreSQL en volumen EBS) → S3 (imágenes y copias), SES, Parameter Store, CloudWatch; GitHub Actions → ECR y SSM;
  - texto de la sección de producción y de las diferencias, coherente con lo implementado (por qué una sola EC2 y no contenedores gestionados, PostgreSQL en la instancia y no RDS, CloudFront sin WAF porque el plan de AWS del proyecto no admite el plan gratuito de CloudFront ni WAF, con límite de peticiones por IP en nginx, Parameter Store en vez de Secrets Manager, dominio `entrevecinos.org` registrado en Dinahosting con el DNS en Route 53 gestionado por Terraform);
  - **base de datos y disponibilidad**: el nodo del diagrama `PostgreSQL gestionado<br/>alta disponibilidad + backups` pasa a `PostgreSQL 16 en la instancia<br/>volumen EBS + copias cada 6 h en S3`, y la frase «una instancia gestionada, preferiblemente con alta disponibilidad, copias de seguridad y recuperación a un punto en el tiempo» se sustituye por la decisión real: **PostgreSQL en la instancia y sin alta disponibilidad para ahorrar costes mientras el proyecto no escale**, sus mitigaciones (copias cada 6 h, alarma de copias, volumen separado, usuario sin privilegios), RPO de 6 h (TK-092), enlazando a la decisión de `infra/aws/README.md` (TK-082); el resumen de todas las decisiones y la evolución recomendada los añade TK-095;
  - **integración y despliegue continuos:** subsección breve que resuma qué se comprueba en cada *pull request* (`ci.yml`: `api`, `web`, `infra`, `images`, `docs-infra`; obligatorias para fusionar en `main`) y qué ocurre al fusionar (`deploy.yml`: `checks` → `publish` → `deploy` → `smoke`, vuelta atrás visible si la API no arranca, un despliegue cada vez, redespliegue manual de un commit de `main`), enlazando a «Integración continua» y «Despliegue continuo» de `infra/aws/README.md` en vez de repetir el detalle; sustituye la frase genérica «una canalización CI/CD puede construir y publicar imágenes…» de las diferencias técnicas;
  - se elimina la nota «Pendiente».
- `readme.md` §2.5: medidas de seguridad que ya son reales en producción (HTTPS en CloudFront, límite de peticiones por IP en el proxy, cabecera de origen, IMDSv2, sin SSH, roles con mínimo privilegio, credenciales temporales en el despliegue (un usuario de CI que solo asume el rol de despliegue, desde el entorno `production` limitado a `main`, TK-088), comprobaciones obligatorias antes de fusionar en `main` (TK-089), PostgreSQL solo en la red interna de Compose con usuario sin privilegios, copias que la instancia no puede borrar, secretos en Parameter Store que solo llegan a los contenedores por entorno, sin ficheros `.env` en la instancia, bucket privado).
- `infra/aws/README.md` (guía completa):
  - requisitos (`aws login --profile entrevecinos`, Docker), estructura y *bootstrap*;
  - orden de aplicación y primer despliegue manual (de TK-078 a TK-087), pasos manuales (verificación de SES, suscripciones de SNS, salida del *sandbox*, protección de `main`);
  - variables de `prod.tfvars` y salidas;
  - **DNS en Route 53:** lista de los registros que crea Terraform (TK-084 y TK-087), la regla de no crear registros a mano y el **procedimiento de delegación** desde Dinahosting (fase 0, cambio de servidores de nombres, comprobaciones con `dig` y cómo volver a los servidores de Dinahosting si algo falla);
  - **gestión de secretos:** dónde vive cada uno (`/entrevecinos/prod/…`), cómo llegan a los contenedores (solo por entorno, TK-086), el riesgo residual de `docker inspect` y la regla de no crear nunca un `.env` en la instancia;
  - **runbook**:
    - nombrar un `platform_admin` (sesión de SSM → `docker compose exec db psql -U entrevecinos_app entrevecinos` → `UPDATE users SET platform_role = 'platform_admin' WHERE email = …`);
    - desplegar un SHA concreto y volver a una versión anterior (`workflow_dispatch`);
    - rotar `JWT_SECRET` (invalida sesiones) y la cabecera de origen (nueva versión del parámetro y `deploy.sh`, que recrea los contenedores con los valores nuevos; los secretos no están en ningún fichero que editar), y rotar a mano las contraseñas de PostgreSQL (sin rotación automática, TK-082: nueva versión del parámetro, `ALTER ROLE … PASSWORD` y volver a desplegar);
    - actualizar PostgreSQL: versión menor (copia previa y `deploy.sh`) y versión mayor (`pg_dump`, volumen nuevo, `pg_restore`);
    - **migrar a RDS** cuando el proyecto escale (`pg_dump` / `pg_restore`, nuevo `DATABASE_URL`, corte de minutos);
    - reemplazar la instancia (nueva AMI) sin perder datos: el volumen de datos de TK-082 se desacopla y se vuelve a adjuntar;
    - responder a cada alarma de TK-091;
    - restaurar copias (TK-092);
    - renovar la sesión de `aws login` y qué hacer ante `AccessDenied` repentinos (*spend limit*);
  - **costes**: límite de gasto de 40 €/mes (TK-078) y su equivalente en USD, estimación mensual por servicio y cómo consultarla;
  - **destruir el entorno** para no gastar créditos: orden (`prevent_destroy` y `disable_api_termination` primero), copia final de la base con `backup.sh` y qué no se borra (bucket de estado y, si se quiere, el de copias).
- `infra/README.md`: enlace a `infra/aws/README.md` y a `docker-compose.prod.yml`.
- `AGENTS.md`: comandos `make tf-*`, ubicación de `infra/aws/` y `.github/workflows/`, y la regla de no aplicar Terraform sin confirmación.
- `.env.example`: bloque comentado con las variables de producción (sin valores reales).

**No incluye**
- Documentación del código de la API o de la web (sin cambios funcionales).

## 3. Requisitos técnicos

- El diagrama se renderiza sin errores en GitHub (como HU-33 AC4).
- Los comandos de la guía se copian y ejecutan tal cual, con marcadores `<…>` solo donde el valor depende del despliegue.
- Ningún secreto, ARN de secreto con sufijo aleatorio ni contraseña en la documentación.

## 4. Criterios de aceptación

**AC1 — Arquitectura real (HU-38 AC4)**
- **Given** `readme.md` §2.4
- **When** comparo el diagrama con los recursos de Terraform
- **Then** cada componente del diagrama existe en `infra/aws/` y no aparece ningún componente que no exista (balanceador, API Gateway, RDS, Secrets Manager), la base de datos figura como PostgreSQL en la instancia, se explica que es para ahorrar costes mientras el proyecto no escale, y no queda la nota «Pendiente»

**AC2 — Guía reproducible (HU-36 AC1, HU-38 AC4)**
- **Given** una persona con acceso al proyecto de AWS que no ha participado en la épica
- **When** sigue `infra/aws/README.md`
- **Then** puede crear el entorno, desplegar, nombrar un `platform_admin`, volver a una versión anterior y destruir el entorno sin ayuda

**AC3 — Agentes**
- **Given** `AGENTS.md`
- **When** un agente busca cómo validar o aplicar la infraestructura
- **Then** encuentra los comandos y la obligación de pedir confirmación antes de `terraform apply` o `destroy`

**AC4 — Integración y despliegue continuos (HU-37)**
- **Given** `readme.md` §2.4
- **When** busco qué se comprueba en un *pull request* y qué pasa al fusionarlo en `main`
- **Then** encuentro las comprobaciones de CI y los pasos del despliegue, coherentes con `.github/workflows/ci.yml` y `deploy.yml`, y el enlace a la guía de `infra/aws/README.md` con el detalle y el *runbook*

## 5. Plan de tareas

1. Diagrama y texto de `readme.md` §2.4 (incluida la integración y el despliegue continuos) y §2.5.
2. `infra/aws/README.md`: guía, runbook, costes y destrucción.
3. `infra/README.md`, `AGENTS.md` y `.env.example`.
4. Revisión cruzada con los recursos reales y prueba de la guía por otra persona (o en una cuenta limpia).

## 6. Verificación

```bash
# Diagrama: vista previa del readme en GitHub, sin errores de Mermaid
grep -n "Pendiente" readme.md          # sin resultados en §2.4
grep -n "canalización CI/CD puede" readme.md   # sin resultados: sustituida por la descripción real
grep -n "ci.yml\|deploy.yml" readme.md        # integración y despliegue continuos en §2.4
grep -n -i "alta disponibilidad" readme.md   # ninguna referencia a la base de datos de producción
grep -n -i "mientras el proyecto no escale" readme.md infra/aws/README.md   # decisión documentada en ambos
grep -n -i "RDS\|Secrets Manager" readme.md   # solo como evolución futura
grep -rnE "AKIA|password=|secret=" readme.md infra/ AGENTS.md .env.example   # sin secretos reales
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Diagrama renderizado en GitHub.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Documentación que envejece:** se resuelve en TK-094 (reglas en `openspec/config.yaml` y `AGENTS.md` y comprobación en CI).
- **Arquitectura distinta de la prevista:** el registro de decisiones (coste, mientras el proyecto no escale) y la evolución recomendada se documentan en TK-095.
