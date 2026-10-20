# TK-045 · Frontend: reservar, quitar la reserva y finalizar desde el detalle

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`ListingActions`, detalle del anuncio, `ListingCard`) |
| **Historia** | HU-09b Marcar mi anuncio como reservado o finalizado (Épica 3) |
| **Prioridad** | Media |
| **Depende de** | TK-018 (`ConfirmDialog`), TK-025, TK-037, TK-044 |
| **Referencias** | `user-stories.md` HU-09b |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-09b pide que el autor marque su anuncio como reservado o finalizado, que pueda quitar la reserva y que nadie más tenga esas opciones. El listado (TK-029) y el detalle (TK-037) ya muestran la etiqueta «Reservado», pero hasta ahora nada podía poner un anuncio en ese estado.

**Objetivo:** añadir al detalle del anuncio los botones «Marcar como reservado», «Quitar reserva» y «Marcar como finalizado», visibles solo para el autor.

## 2. Alcance

**Incluye**
- Botones en `ListingActions` según `isOwner` y `status`.
- Confirmación al finalizar.
- *Server Action* `changeListingStatus(listingId, status)`.
- Aviso «Este anuncio está finalizado.» en el detalle y ocultación de «Editar» en anuncios finalizados.

**No incluye**
- Cambiar el estado desde el listado o desde «Mis anuncios» (asumido: el detalle es el único punto de entrada, como editar y eliminar).
- Retirar y restaurar (TK-043).

## 3. Requisitos técnicos

### 3.1 Botones (solo si `isOwner`)

| Estado | Acciones de estado | Confirmación |
|---|---|---|
| `active` | «Marcar como reservado», «Marcar como finalizado» | solo al finalizar |
| `reserved` | «Quitar reserva», «Marcar como finalizado» | solo al finalizar |
| `completed` | ninguna | — |
| `hidden` | ninguna (aviso de TK-043) | — |

- Convivencia con el resto de acciones: «Editar» (TK-025) se oculta en `completed` y `hidden`; «Eliminar» (TK-027) se mantiene; si además soy administrador, «Retirar anuncio» (TK-043) aparece en su propio grupo.
- Confirmación de finalizar (`ConfirmDialog`): «¿Marcar este anuncio como finalizado? Dejará de mostrarse en el listado y no podrás volver a activarlo ni editarlo.», botón «Marcar como finalizado».
- Cada botón es un `<form action>` con `useFormStatus` para deshabilitarse mientras se envía; funciona sin JavaScript salvo la confirmación, que en ese caso se omite (asumido, igual que TK-027).

### 3.2 *Server Action* `changeListingStatus`

- `requireUser()`; valida `listingId` (UUID) y `status` (`active` | `reserved` | `completed`) con zod.
- `PATCH /v1/listings/{id}/status`; comparte la llamada con `moderateListing` de TK-043 (una función `patchListingStatus` en `features/listings/api.ts`) si ese ticket ya está hecho.
- Éxito: `revalidatePath` del detalle y del listado de la comunidad; se queda en el detalle con el mensaje (`role="status"`):
  - reservar → «Anuncio marcado como reservado.»
  - quitar la reserva → «El anuncio vuelve a estar disponible.»
  - finalizar → «Anuncio finalizado. Ya no se muestra en el listado.»
- Errores: `409` y `403` → mensaje de la API en una alerta (`role="alert"`); red o `5xx` → «No se ha podido cambiar el estado. Inténtalo de nuevo.».

### 3.3 Estado en el detalle y en el listado

- `reserved`: etiqueta «Reservado» (ya existe en TK-029 y TK-037).
- `completed`: etiqueta «Finalizado» y aviso «Este anuncio está finalizado.» (`role="status"`) en el detalle, visible para cualquier miembro que llegue por el enlace (TK-036 lo permite).

### 3.4 Pruebas

- `ListingActions`: matriz de §3.1 con `isOwner` verdadero y falso, y combinada con `canModerate`.
- Confirmación: finalizar no se envía si se cancela.
- `changeListingStatus`: éxito por cada transición, `409`, `403`, error de red, `status` no válido rechazado por zod.
- Detalle: etiqueta y aviso de finalizado; sin «Editar» en `completed`.

## 4. Criterios de aceptación

**AC1 — Reservar (HU-09b AC1)**
- **Given** que soy el autor de un anuncio activo y estoy en su detalle
- **When** pulso «Marcar como reservado»
- **Then** veo «Anuncio marcado como reservado.» y la etiqueta «Reservado» en el detalle y en el listado

**AC2 — Quitar la reserva (HU-09b AC2)**
- **Given** que soy el autor de un anuncio reservado
- **When** pulso «Quitar reserva»
- **Then** desaparece la etiqueta «Reservado» y vuelvo a ver «Marcar como reservado»

**AC3 — Finalizar (HU-09b AC3)**
- **Given** que soy el autor de un anuncio activo o reservado
- **When** pulso «Marcar como finalizado» y confirmo
- **Then** veo el aviso de finalizado, sin botones de estado ni «Editar», y el anuncio ya no aparece en el listado ni en las búsquedas

**AC4 — Solo el autor (HU-09b AC4)**
- **Given** el detalle de un anuncio de otro vecino, aunque sea administrador de la comunidad
- **When** reviso las acciones disponibles
- **Then** no veo «Marcar como reservado», «Quitar reserva» ni «Marcar como finalizado»

## 5. Plan de tareas

1. *Server Action* `changeListingStatus` con pruebas.
2. Botones en `ListingActions` y confirmación de finalizar.
3. Etiqueta y aviso de finalizado; ocultar «Editar» en `completed`.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Autor: detalle → «Marcar como reservado» → etiqueta en detalle y listado → «Quitar reserva»
# Autor: «Marcar como finalizado» → confirmar → aviso, sin «Editar»; el listado y la búsqueda ya no lo muestran
# Otro miembro (y un administrador no autor): detalle → sin botones de estado
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Los botones son accesibles con teclado y anuncian el resultado a los lectores de pantalla.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Finalizar por error:** es irreversible (TK-044 §8); la confirmación lo advierte de forma explícita.
- **Anuncios finalizados del autor:** solo se encuentran por su enlace; una página «Mis anuncios» (sin historia) los listaría.
