# TK-094 · Documentación: regla para mantener `infra/aws/README.md` al día

| Campo | Valor |
|---|---|
| **Tipo** | Documentación / proceso |
| **Componente** | `openspec/config.yaml`, `AGENTS.md`, `.github/pull_request_template.md` (nuevo), `infra/aws/README.md` (esqueleto), `infra/README.md`; `.github/workflows/ci.yml` en TK-089 |
| **Historia** | HU-39 Entender las decisiones de la arquitectura de producción y mantener su documentación al día (Épica 13) |
| **Prioridad** | Alta (adelantarlo justo después de TK-078; ver §8) |
| **Depende de** | — (crea el esqueleto de `infra/aws/README.md`, que TK-078 amplía) |
| **Referencias** | TK-093 §8 («Documentación que envejece»); `openspec/config.yaml` (`context` y `rules`); `AGENTS.md` (§Convenciones) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`infra/aws/README.md` es la guía para crear, desplegar, operar y destruir producción (TK-093) y el registro de decisiones de arquitectura (TK-082, TK-095). Si un cambio en Terraform, en el Compose de producción, en los *scripts* de la instancia o en los *workflows* no la actualiza, la guía deja de ser fiable sin que nadie lo note. Hoy ninguna regla del proyecto lo exige: `openspec/config.yaml` solo describe el Compose de desarrollo y `AGENTS.md` no menciona la infraestructura de AWS.

**Objetivo:** que todo cambio de la infraestructura actualice `infra/aws/README.md` en el mismo cambio, exigido por las reglas de OpenSpec, por las instrucciones de los agentes y por la plantilla de *pull request*.

**Alcance reducido (decisión del proyecto):** se implementa antes que el resto de la épica, cuando aún no existen `infra/aws/` ni `.github/workflows/`. Por eso este ticket crea el esqueleto de `infra/aws/README.md` y la **comprobación automática `docs-infra` se traslada a TK-089** (HU-39 AC2), que crea el primer *workflow*.

## 2. Alcance

**Incluye**
- **Rutas de infraestructura** (definición única, reutilizada en las tres reglas): `infra/aws/**`, `infra/prod/**`, `infra/docker-compose.prod.yml` y `.github/workflows/**`.
- **`openspec/config.yaml`:**
  - `context`: añadir la infraestructura de producción (Terraform en `infra/aws/`, Compose de producción y *scripts* de `infra/prod/`, *workflows* de GitHub Actions) y que `infra/aws/README.md` es la guía de operación y el registro de decisiones;
  - `rules.proposal`: «En Impact, si el change toca las rutas de infraestructura, indicarlo y citar las secciones de `infra/aws/README.md` afectadas.»;
  - `rules.design`: «Si el change modifica una decisión de arquitectura de producción, actualizar su entrada en la sección "Decisiones de arquitectura" de `infra/aws/README.md` (TK-095).»;
  - `rules.tasks`: «Si el change toca las rutas de infraestructura, incluir en el grupo Documentación una tarea que actualice `infra/aws/README.md` (guía, *runbook*, costes o decisiones, según corresponda).».
- **`AGENTS.md`:** nueva viñeta en §Convenciones, junto a «Contrato» y «Esquema»:
  > **Infraestructura:** si cambias `infra/aws/`, `infra/prod/`, `infra/docker-compose.prod.yml` o `.github/workflows/`, actualiza `infra/aws/README.md` en el mismo cambio (guía, *runbook*, costes y, si cambia una decisión, «Decisiones de arquitectura»).
- **Esqueleto de `infra/aws/README.md`** con una sección por tema (estructura, puesta en marcha, despliegue, DNS, secretos, operación, costes, decisiones de arquitectura, evolución, destrucción) y el ticket que completará cada una; enlace desde `infra/README.md`.
- ~~**Comprobación en CI**~~ **trasladada a TK-089** (trabajo `docs-infra`; se conserva aquí la definición para referencia):
  - compara los ficheros cambiados del *pull request* con la rama base;
  - si alguno está en las rutas de infraestructura y `infra/aws/README.md` no ha cambiado, falla con el mensaje «Este *pull request* cambia la infraestructura: actualiza `infra/aws/README.md` o añade la etiqueta `sin-cambios-en-doc-infra` si el cambio no afecta a la documentación.»;
  - la etiqueta `sin-cambios-en-doc-infra` lo omite (p. ej. un cambio de formato o una versión de una acción); se crea en el repositorio;
  - se añade a los *status checks* obligatorios de `main` (TK-089).
- **Plantilla de *pull request*** (`.github/pull_request_template.md`) con la casilla «Si cambia la infraestructura, he actualizado `infra/aws/README.md`.».

**No incluye**
- El contenido de `infra/aws/README.md` (TK-093) ni el registro de decisiones (TK-095).
- Comprobar que el contenido de la guía es correcto (lo hace la revisión del *pull request*).

## 3. Requisitos técnicos

- El trabajo `docs-infra` no necesita secretos ni acceso a AWS; usa `git diff --name-only origin/<base>...HEAD` (con `fetch-depth: 0`) o una acción de detección de cambios fijada por SHA.
- En *push* a `main` el trabajo no se ejecuta (solo tiene sentido en *pull requests*).
- Las reglas de `openspec/config.yaml` siguen el estilo de las existentes: en español, una frase por regla.
- El YAML sigue siendo válido (`openspec` lo carga sin errores).

## 4. Criterios de aceptación

**AC1 — Regla en OpenSpec (HU-39 AC1)**
- **Given** `openspec/config.yaml`
- **When** se genera un change cuyo alcance toca las rutas de infraestructura (`/opsx:propose`)
- **Then** su *proposal* lo indica en Impact y su `tasks.md` incluye una tarea de Documentación que actualiza `infra/aws/README.md`

**AC2 — Regla para agentes (HU-39 AC1)**
- **Given** `AGENTS.md`
- **When** lo leo en §Convenciones
- **Then** encuentro la viñeta «Infraestructura» con las rutas y la obligación de actualizar `infra/aws/README.md`

**AC3 — Comprobación en CI (HU-39 AC2; se verifica en TK-089, AC2b)**
- **Given** un *pull request* que cambia `infra/aws/modules/network/main.tf` sin tocar `infra/aws/README.md`
- **When** termina CI
- **Then** el trabajo `docs-infra` falla con el mensaje acordado y el *pull request* no se puede fusionar; con la etiqueta `sin-cambios-en-doc-infra`, o actualizando la guía, pasa

**AC4 — Sin falsos positivos (se verifica en TK-089, AC2b)**
- **Given** un *pull request* que solo cambia `apps/web/`
- **When** termina CI
- **Then** `docs-infra` pasa

## 5. Plan de tareas

1. Reglas y contexto en `openspec/config.yaml`.
2. Viñeta en `AGENTS.md`.
3. Plantilla de *pull request*.
4. Esqueleto de `infra/aws/README.md` y enlace desde `infra/README.md`.
5. Actualizar TK-089 con el trabajo `docs-infra` (sus AC verifican AC3 y AC4).
6. Prueba de AC1 con las instrucciones de OpenSpec.

## 6. Verificación

```bash
openspec validate --all                       # la configuración carga sin errores (asumido: comando del CLI de OpenSpec)
grep -n "infra/aws/README.md" openspec/config.yaml AGENTS.md
```

En GitHub (interfaz web): un *pull request* de prueba que toca `infra/aws/` sin la guía muestra `docs-infra` en rojo con el mensaje; tras añadir la etiqueta o la guía, en verde. En *Settings* → *Branches*, `docs-infra` figura como obligatorio.

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen (AC3 y AC4, con la comprobación de CI de TK-089).
- [x] Cambios revisados y fusionados mediante *pull request* (#6).

## 8. Riesgos y decisiones abiertas

- **Momento de implementarlo:** se implementa el primero de la épica para que TK-078 a TK-093 ya estén sujetos a la regla; la comprobación automática llega con TK-089.
- **La comprobación solo detecta ausencia, no calidad:** un cambio trivial en la guía la satisface. Se complementa con la casilla de la plantilla y la revisión del *pull request*.
- **Etiqueta de omisión usada de más:** se revisa en el *pull request*; si se abusa, exigir un comentario que justifique la etiqueta.
