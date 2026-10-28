## Context

HU-17 y TK-043 introdujeron la moderación con el verbo «Retirar».

## Decisions

- **Solo textos visibles:** los nombres internos (`hidden`, `RETIRED`), los comentarios y los tickets anteriores no cambian.

## Risks / Trade-offs

- [La web reconoce el bloqueo por el texto de la API (`/ocultado|finalizado/`)] → cambiar el mensaje exige actualizar ambos lados a la vez.
