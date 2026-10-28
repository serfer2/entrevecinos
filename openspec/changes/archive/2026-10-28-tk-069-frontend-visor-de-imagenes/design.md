## Context

TK-037 muestra la imagen principal en media columna y miniaturas.

## Decisions

- **`<dialog>` con `showModal()`:** atrapa el foco, lo devuelve al cerrar y Escape lo cierra sin código propio.
- **Índice compartido con la galería:** al cerrar, el detalle muestra la última imagen vista.
- **Gestos con *pointer events* y `touch-action: pan-y`:** la imagen sigue al dedo y cambia con más de 50 px horizontales que superen al vertical; el clic final de un arrastre no cierra el visor. `setPointerCapture` es opcional.
- **Fuera de alcance:** zoom dentro de la imagen y precarga de las vecinas.

## Risks / Trade-offs

- [Gestos probados con eventos simulados] → conviene probarlo en un móvil real.
