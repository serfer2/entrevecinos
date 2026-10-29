# TK-075 · Documentación: alcance del MVP en el modelo de datos y en el README

| Campo | Valor |
|---|---|
| **Tipo** | Documentación |
| **Componente** | `readme.md` (§1.2, §3.1, §3.2, §4), `docs/product/user-stories.md` |
| **Historia** | HU-34 Distinguir qué parte del modelo de datos y de la API pertenece al MVP (Épica 12) |
| **Prioridad** | Media |
| **Depende de** | TK-074 |
| **Referencias** | Tabla entidades ↔ rutas de TK-074 §1; `apps/api/src/entrevecinos/infrastructure/db/models/` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El modelo de datos de `readme.md` §3 describe 15 entidades «para las funciones descritas en el README», sin distinguir las 8 que tienen tabla en el MVP de las 7 previstas para versiones futuras. §1.2 enumera las funciones aplazadas, pero no las relaciona con las entidades ni con la API.

**Objetivo:** que quien lea el README sepa qué entidades y qué partes de la API forman el MVP y cuáles están pendientes.

## 2. Alcance

**Incluye**
- §3.1, diagrama ER: comentario de cada entidad futura con «Versión futura» (p. ej. `CONVERSATION` …), y una nota bajo el diagrama con las entidades del MVP y las futuras.
- §3.2:
  - Párrafo inicial: el modelo cubre el MVP y las versiones futuras; tabla «Entidad | Alcance | Rutas de la API» (la de TK-074 §1, sin la columna de tabla implementada).
  - Encabezado de cada entidad futura con «(versión futura)»: `conversation`, `message`, `notification`, `professional_profile`, `professional_service`, `professional_profile_image`, `report`.
  - Tipos enumerados e índices que solo usan entidades futuras, marcados igual.
- §1.2: en «Quedan para una fase posterior…», remitir a las entidades y operaciones marcadas como versión futura.
- §4: una frase que explique `x-mvp` y remita al resumen de `docs/api/README.md` (el resto de §4 es de TK-077).
- `docs/product/user-stories.md`, «Fuera de alcance»: remitir al modelo de datos y al contrato para el detalle.

**No incluye**
- Cambios de esquema o migraciones.
- Los tickets copiados en §6 del README.

## 3. Requisitos técnicos

- Los diagramas Mermaid siguen siendo válidos (en `erDiagram`, «Versión futura» va en el comentario del atributo `id` o en una nota fuera del diagrama, porque no admite estilos por entidad (asumido)).
- Los nombres de entidades y rutas se copian del contrato y de los modelos, no de los tickets.
- Mismo estilo que el resto del README.

## 4. Criterios de aceptación

**AC1 — Entidades marcadas (HU-34 AC3)**
- **Given** `readme.md` §3
- **When** leo cualquier entidad
- **Then** sé si es del MVP o de una versión futura

**AC2 — Entidades y rutas (HU-34 AC1)**
- **Given** la tabla de §3.2
- **When** la comparo con el contrato
- **Then** cada entidad del MVP tiene sus rutas `x-mvp: true` y cada entidad futura solo rutas `x-mvp: false`

**AC3 — Coherencia con §1.2**
- **Given** las funciones aplazadas de §1.2
- **When** busco sus entidades y rutas
- **Then** todas aparecen marcadas como versión futura

## 5. Plan de tareas

1. §3.1 (diagrama y nota).
2. §3.2 (tabla, encabezados, enumerados e índices).
3. §1.2, §4 y `user-stories.md`.
4. Renderizar el diagrama ER.

## 6. Verificación

```bash
grep -n -i "versión futura" readme.md
# Renderizar el diagrama ER de §3.1 con mermaid-cli (ver TK-073 §6)
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Diagramas Mermaid válidos.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **`users.avatar_asset_id` y otros campos sin uso en el MVP:** se documentan como están; marcar campos sueltos queda fuera (asumido).
