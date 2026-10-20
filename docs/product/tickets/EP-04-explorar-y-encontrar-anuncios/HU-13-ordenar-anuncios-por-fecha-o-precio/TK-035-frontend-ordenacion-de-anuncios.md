# TK-035 · Frontend: ordenar el listado por fecha o precio

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`ListingFilters`, `ListingSearchParams`) |
| **Historia** | HU-13 Ordenar anuncios por fecha o precio (Épica 4) |
| **Prioridad** | Media |
| **Depende de** | TK-033, TK-034 |
| **Referencias** | `user-stories.md` HU-13 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-13 pide ordenar el listado por fecha o por precio, en los dos sentidos.

**Objetivo:** añadir a `ListingFilters` un selector de orden que combine `sort` y `order` en opciones comprensibles.

## 2. Alcance

**Incluye**
- `<select name="orden">` con cuatro opciones, traducido a `sort` y `order` al llamar a la API.
- Conservación del orden en la paginación, la búsqueda, los filtros y el selector de comunidad.

## 3. Requisitos técnicos

| Opción (valor en la URL) | Texto | API |
|---|---|---|
| `recientes` (por defecto) | Más recientes | `sort=published_at&order=desc` |
| `antiguos` | Más antiguos | `sort=published_at&order=asc` |
| `precio-asc` | Precio: de menor a mayor | `sort=price&order=asc` |
| `precio-desc` | Precio: de mayor a menor | `sort=price&order=desc` |

- La URL usa un único parámetro legible `orden` (asumido); `ListingSearchParams` lo traduce. Un valor desconocido se trata como `recientes`.
- Con un orden por precio, se muestra la nota «Los anuncios sin precio aparecen al final.» (HU-13 AC3).
- Mismo envío automático progresivo que los filtros (TK-033).

### Pruebas

- Traducción de `orden` a `sort`/`order` (incluido el valor por defecto y uno inválido).
- Conservación de `orden` en las URLs de paginación, «Limpiar» y cambio de comunidad.

## 4. Criterios de aceptación

**AC1 — Por fecha (HU-13 AC1)**
- **Given** el listado de mi comunidad
- **When** elijo «Más recientes» o «Más antiguos»
- **Then** los anuncios se ordenan por fecha en ese sentido

**AC2 — Por precio (HU-13 AC2)**
- **Given** el listado
- **When** elijo «Precio: de menor a mayor» o «de mayor a menor»
- **Then** los anuncios se ordenan por precio en ese sentido

**AC3 — Sin precio al final (HU-13 AC3)**
- **Given** anuncios sin precio
- **When** ordeno por precio
- **Then** aparecen al final y veo la nota que lo explica

## 5. Plan de tareas

1. `orden` en `ListingSearchParams` con pruebas.
2. Selector en `ListingFilters` y conservación en todas las URLs.
3. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# /comunidades/<id> → «Precio: de menor a mayor» → orden correcto y regalos al final; ir a la página 2 → mismo orden
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- Ninguno relevante.
