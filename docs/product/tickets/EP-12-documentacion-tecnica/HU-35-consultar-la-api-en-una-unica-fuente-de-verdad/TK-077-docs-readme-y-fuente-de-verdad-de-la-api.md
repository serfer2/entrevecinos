# TK-077 · Documentación: el README remite a `docs/api/openapi.yaml` y su fragmento coincide

| Campo | Valor |
|---|---|
| **Tipo** | Documentación |
| **Componente** | `readme.md` (§4 Especificación de la API) |
| **Historia** | HU-35 Consultar la API en una única fuente de verdad (Épica 12) |
| **Prioridad** | Media |
| **Depende de** | TK-074 |
| **Referencias** | `docs/api/openapi.yaml`, `docs/api/README.md`; TK-058 (cambio incompatible de `registerUser`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`readme.md` §4 incluye un OpenAPI propio, escrito antes del contrato de `docs/api/`, con tres rutas (`/communities/{community_id}/listings`, `/auth/register`, `/auth/token`) y sus esquemas. No menciona `docs/api/openapi.yaml` y ya no coincide con él; por ejemplo:

- `/auth/register` dice que «devuelve un token JWT» y responde `AuthResponse`; el contrato responde `RegistrationResponse` sin token y `409` con `RegistrationConflict` (TK-058, TK-059).
- Faltan `operationId`, `x-mvp` y las respuestas comunes (`MembershipForbidden`, `ValidationError`…).

**Objetivo:** que §4 declare `docs/api/openapi.yaml` como fuente de verdad y que el fragmento sea un extracto fiel de él.

## 2. Alcance

**Incluye**
- Párrafo inicial de §4: el contrato completo está en [`docs/api/openapi.yaml`](docs/api/openapi.yaml), que es la fuente de verdad; enlace a `docs/api/README.md` (estructura, convenciones, lint, previsualización y resumen MVP / versiones futuras).
- Sustituir el fragmento por un extracto del contrato *bundled* con las mismas tres rutas (`listCommunityListings`, `createListing`, `registerUser`, `loginUser`) y los componentes que referencian, sin editar a mano.
- Encabezado del bloque: «Extracto de `docs/api/openapi.yaml`; si difieren, prevalece el contrato.».
- Revisar el texto de §4 sobre contacto y mensajería, coherente con TK-074 y TK-075.

**No incluye**
- Cambios en el contrato (salvo los de TK-074).
- Una comprobación automática en CI del fragmento (ver §8).

## 3. Requisitos técnicos

- Generar el extracto a partir del bundle (`redocly bundle`) filtrando esas rutas y los `components` a los que llegan sus `$ref`; documentar el comando en `docs/api/README.md` para regenerarlo.
- El bloque sigue siendo YAML válido y OpenAPI 3.1 válido por sí mismo (lint del extracto).
- Se conservan `info` y `servers` del contrato.

## 4. Criterios de aceptación

**AC1 — Fuente de verdad (HU-35 AC1)**
- **Given** `readme.md` §4
- **When** lo leo
- **Then** encuentro el enlace a `docs/api/openapi.yaml` indicado como fuente de verdad y el enlace a `docs/api/README.md`

**AC2 — Fragmento coherente (HU-35 AC2)**
- **Given** el extracto de §4
- **When** lo comparo con las mismas operaciones del bundle
- **Then** son idénticas en rutas, parámetros, cuerpos, respuestas y esquemas

**AC3 — Extracto válido**
- **Given** el extracto
- **When** lo valido con `redocly lint`
- **Then** no hay errores

## 5. Plan de tareas

1. Comando de extracción y documentación en `docs/api/README.md`.
2. Párrafo de §4 y extracto.
3. Lint del extracto y comparación con el bundle.

## 6. Verificación

```bash
cd docs/api
npx @redocly/cli bundle openapi.yaml -o dist/openapi.bundled.yaml
# Extraer el bloque YAML de readme.md §4 a /tmp/readme-api.yaml y validarlo:
npx @redocly/cli lint /tmp/readme-api.yaml
# Comparar cada operación del extracto con la del bundle (diff de YAML normalizado)
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Lint del extracto sin errores.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **El extracto puede volver a quedarse atrás:** se mitiga con el encabezado («prevalece el contrato») y el comando documentado. Alternativa: sustituir el extracto por solo un enlace; se mantiene porque §4 del README pide incluir la especificación (asumido).
- **Comprobación automática:** una prueba que compare el extracto con el contrato puede añadirse a TK-076 si se quiere; no se incluye para no acoplar las pruebas de la API al `readme.md`.
