# TK-031 · Frontend: buscador de anuncios por palabras clave

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/components/ListingFilters.tsx`, página de la comunidad) |
| **Historia** | HU-11 Buscar anuncios por palabras clave (Épica 4) |
| **Prioridad** | Media |
| **Depende de** | TK-029, TK-030 |
| **Referencias** | `user-stories.md` HU-11 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-11 pide un buscador en el listado de la comunidad, un mensaje cuando no hay resultados y poder borrar la búsqueda para volver a ver todos los anuncios.

**Objetivo:** añadir la barra de búsqueda al listado (`?q=`), que será el contenedor de los filtros y el orden de TK-033 y TK-035.

## 2. Alcance

**Incluye**
- Componente `ListingFilters` (formulario GET) con el campo de búsqueda y los botones «Buscar» y «Limpiar».
- Mensaje de resultados y de «sin resultados».
- `ListingSearchParams` (TK-029) con `q`.

**No incluye**
- Filtros por tipo y comunidad (TK-033) y orden (TK-035).

## 3. Requisitos técnicos

### 3.1 Formulario

- `<form method="get" role="search">` con `<input type="search" name="q" minLength={2} maxLength={160}>` y etiqueta «Buscar anuncios» (visible o con `aria-label`).
- Al buscar, la página vuelve a la 1 (no se envía `page`). La URL refleja la búsqueda, así que se puede compartir y funciona sin JavaScript.
- «Limpiar» es un enlace a la página de la comunidad sin `q` (y, en adelante, conservando el resto de filtros, asumido).
- El valor del campo se rellena desde la URL.
- **Mínimo 2 caracteres (HU-11 AC4):** `minLength` valida en el navegador; si llega `?q=` de 1 carácter (URL escrita a mano o sin validación nativa), la página no llama a la API con ese `q`, muestra «La búsqueda debe tener al menos 2 caracteres.» junto al campo (`aria-describedby`) y mantiene el listado sin filtrar. Un `422` de la API por `q` se trata igual.

### 3.2 Resultados

- Con `q`: «<total> resultados para "<q>"» (`aria-live="polite"`).
- Sin resultados: «No hay anuncios que coincidan con "<q>".» y el enlace «Ver todos los anuncios». Es distinto del estado vacío de una comunidad sin anuncios (TK-029).
- La paginación conserva `q`.

### 3.3 Pruebas

- `ListingSearchParams`: `q` recortado, vacío ignorado, de 1 carácter marcado como inválido, más de 160 caracteres recortado.
- `ListingFilters`: valor inicial, enlace «Limpiar».
- Página: mensaje de resultados, sin resultados frente a comunidad vacía, paginación con `q`.

## 4. Criterios de aceptación

**AC1 — Coincidencias (HU-11 AC1)**
- **Given** que estoy en el listado de mi comunidad
- **When** escribo «bici» y busco
- **Then** veo solo los anuncios cuyo título o descripción la contienen, y el número de resultados

**AC2 — Sin resultados (HU-11 AC2)**
- **Given** el listado
- **When** busco una palabra que no aparece en ningún anuncio
- **Then** veo «No hay anuncios que coincidan con "<palabra>".»

**AC3 — Limpiar (HU-11 AC3)**
- **Given** que he aplicado una búsqueda
- **When** pulso «Limpiar» o vacío el campo y busco
- **Then** vuelvo a ver todos los anuncios de la comunidad

**AC4 — Búsqueda demasiado corta (HU-11 AC4)**
- **Given** el listado
- **When** busco «a»
- **Then** veo «La búsqueda debe tener al menos 2 caracteres.» y el listado no cambia

## 5. Plan de tareas

1. `q` en `ListingSearchParams` con pruebas.
2. `ListingFilters` y mensajes en la página de la comunidad.
3. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# /comunidades/<id> → buscar «bici» → resultados; «patinete» → sin resultados; «Limpiar» → todos
# Copiar la URL con ?q=bici en otra pestaña → mismos resultados
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] La búsqueda funciona sin JavaScript.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Búsqueda mientras se escribe:** no se implementa (requiere *debounce* en el cliente); el envío explícito basta para el MVP.
