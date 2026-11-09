## Context

`rowActions` decide las acciones de cada fila de «Miembros» y `manageMember` las envía a la API según `MEMBER_ACTIONS` (`{ status, done }`; `status: null` expulsa con `DELETE`). Las filas de administradores y la propia no tienen acciones. `requireUser()` ya devuelve `platform_role`.

## Goals / Non-Goals

**Goals:** nombrar y quitar administradores desde la página de miembros, solo para el `platform_admin`.

**Non-Goals:** rol «Moderador»; lista de todas las comunidades en `/admin`; cambios para `community_admin`.

## Decisions

- **`MEMBER_ACTIONS` pasa a `{ body, done }`**: `body` es el cuerpo del `PATCH` (`{ status }` o `{ role }`) o `null` para `DELETE`. Un único punto describe cada acción y `manageMember` no distingue casos.
- **`rowActions(member, currentUserId, isPlatformAdmin = false)`**: la acción de rol se calcula aparte y se antepone a las de estado; las filas propia y de administradores, que antes no tenían acciones, conservan solo la de rol. Sin `isPlatformAdmin`, el resultado es idéntico al actual.
- **Textos de los diálogos en un mapa de la página** (`CONFIRMATIONS`) en lugar de ternarios, al pasar de dos a cuatro acciones con confirmación.
- **Códigos de resultado en la URL** `nombrado-admin` y `quitado-admin`, como los existentes: nunca texto arbitrario en la URL salvo el nombre ya acotado.

## Risks / Trade-offs

- [Ocultar el botón no protege] → la API decide (TK-109): un `community_admin` que forje el formulario recibe `403` y la página muestra el aviso de permisos.
