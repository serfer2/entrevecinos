# TK-033 · Frontend: filtros por tipo y categoría, y selector de comunidad

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`ListingFilters`, `CommunitySwitcher`, página de la comunidad) |
| **Historia** | HU-12 Filtrar anuncios por comunidad y tipo (Épica 4) |
| **Prioridad** | Media |
| **Depende de** | TK-031, TK-032 |
| **Referencias** | `user-stories.md` HU-12; `docs/api/paths/users_me_memberships.yaml`, `categories.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-12 pide filtrar por tipo, cambiar entre mis comunidades y combinar los filtros con la palabra clave.

**Objetivo:** añadir a `ListingFilters` el filtro por tipo y por categoría, y un selector para cambiar entre las comunidades en las que soy miembro aprobado.

## 2. Alcance

**Incluye**
- `<select name="type">` («Todos los tipos» + las seis etiquetas en español) y `<select name="category_id">` («Todas las categorías» + categorías activas).
- `CommunitySwitcher`: lista de mis comunidades aprobadas (`GET /v1/users/me/memberships?status=approved`); al cambiar, navega a `/comunidades/<id>` **conservando** `q`, `type` y `category_id` (asumido: las categorías son globales, así que siguen siendo válidas) y descartando `page`.
- Indicador de filtros activos y «Limpiar filtros».

**No incluye**
- Orden (TK-035).

## 3. Requisitos técnicos

### 3.1 Filtros

- Forman parte del mismo formulario GET que la búsqueda (TK-031): un único botón «Aplicar» envía `q`, `type` y `category_id`; sin JavaScript también funciona. Con JavaScript, cambiar un `<select>` envía el formulario automáticamente (mejora progresiva, `requestSubmit()`).
- `ListingSearchParams` valida `type` contra `ListingType` y `category_id` como UUID; los valores inválidos se ignoran.
- Mensajes: con filtros y sin resultados, «No hay anuncios con estos filtros.» y «Limpiar filtros».

### 3.2 `CommunitySwitcher`

- Solo se muestra si soy miembro aprobado de dos o más comunidades.
- `<select>` con etiqueta «Comunidad»; navegación con un formulario GET a una ruta de redirección `/comunidades/ir?id=<id>&q=…&type=…&category_id=…` (asumido: así funciona sin JavaScript), que valida el id y redirige a `/comunidades/<id>?…`.
- La comunidad actual aparece seleccionada.

### 3.3 Pruebas

- `ListingSearchParams` con `type` y `category_id` válidos e inválidos; construcción de URLs conservando parámetros.
- Ruta `/comunidades/ir`: id válido, inválido y conservación de filtros.
- `ListingFilters`: valores iniciales y «Limpiar filtros».
- `CommunitySwitcher`: oculto con una sola comunidad.

## 4. Criterios de aceptación

**AC1 — Filtro por tipo (HU-12 AC1)**
- **Given** el listado de mi comunidad
- **When** selecciono «Vendo»
- **Then** veo solo anuncios de tipo «Vendo»

**AC2 — Cambio de comunidad (HU-12 AC2)**
- **Given** que soy miembro aprobado de dos comunidades
- **When** elijo la otra en el selector
- **Then** veo únicamente los anuncios de esa comunidad, con los mismos filtros aplicados

**AC3 — Filtros combinados (HU-12 AC3)**
- **Given** que he escrito una palabra clave
- **When** además selecciono un tipo
- **Then** veo solo los anuncios que cumplen ambas condiciones, y la URL refleja los dos parámetros

## 5. Plan de tareas

1. `ListingSearchParams` con `type` y `category_id`, y construcción de URLs.
2. Filtros en `ListingFilters` (con envío automático progresivo).
3. `CommunitySwitcher` y ruta `/comunidades/ir`.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# /comunidades/<id> → «Vendo» → solo Vendo; escribir «bici» → solo Vendo con «bici»
# Selector de comunidad → la otra comunidad con los mismos filtros
# Deshabilitar JavaScript → «Aplicar» sigue funcionando
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] Los filtros funcionan sin JavaScript.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Muchas comunidades:** el selector es un `<select>`; si un usuario perteneciera a muchas, haría falta un buscador.
