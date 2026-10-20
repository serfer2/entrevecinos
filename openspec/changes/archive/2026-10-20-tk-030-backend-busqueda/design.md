## Context

TK-028 dejó `ListingQuery.text` y el filtro de visibilidad común; TK-015 la extensión `unaccent`.

## Goals / Non-Goals

**Goals:** búsqueda en español sin tildes, por prefijo, indexada y segura frente a la entrada del usuario.

**Non-Goals:** ordenar por relevancia; buscar entre comunidades.

## Decisions

- **`es_unaccent`** copia `spanish` y aplica `unaccent` antes de `spanish_stem` a las palabras.
- **Columna `GENERATED ALWAYS … STORED`** con peso A (título) y B (descripción); en el modelo es `Computed` y diferida, así que `alembic check` no detecta diferencias y el ORM nunca la lee ni la escribe.
- **`prefix_tsquery`** (dominio): solo letras y dígitos Unicode, descarta las palabras de un carácter y las une como `palabra:* & …`; el texto del usuario nunca llega sin limpiar a `to_tsquery`. Sin palabras válidas → ninguna coincidencia.
- **Validación en presentación:** `q` recortado; vacío → sin búsqueda (HU-11 AC3); 1 carácter → 422 «La búsqueda debe tener al menos 2 caracteres.»; más de 160 → 422.
- **Criterios aparte de la visibilidad** (`_criteria`): la página y el `total` comparten ambos.

## Risks / Trade-offs

- [Prefijos de 2 caracteres pueden devolver muchos resultados] → aceptable con el volumen de una comunidad.
