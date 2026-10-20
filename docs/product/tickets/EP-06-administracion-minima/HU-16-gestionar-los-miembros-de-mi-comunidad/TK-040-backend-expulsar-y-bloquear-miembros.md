# TK-040 · Backend: listado de miembros, bloqueo y expulsión

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad y seguridad |
| **Componente** | `apps/api/` (área `communities`) |
| **Historia** | HU-16 Gestionar los miembros de mi comunidad (Épica 6) |
| **Prioridad** | Media |
| **Depende de** | TK-017 |
| **Referencias** | `docs/api/paths/communities_community_id_memberships.yaml` (`get`), `communities_community_id_memberships_user_id.yaml` (`patch`, `delete`); esquema `MembershipUpdate` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-16 pide que el administrador vea los miembros con su estado y pueda expulsar o bloquear a quien incumpla las normas, que entonces pierde el acceso a los anuncios, no puede publicar y sus anuncios dejan de mostrarse a los demás miembros. TK-017 dejó el listado y la aprobación; faltan el bloqueo y la expulsión.

**Objetivo:** completar `PATCH …/memberships/{user_id}` con `status: blocked` (y desbloqueo) e implementar `DELETE …/memberships/{user_id}` (expulsión), con las protecciones necesarias.

## 2. Alcance

**Incluye**
- Bloqueo y desbloqueo (`approved ↔ blocked`).
- Expulsión (`DELETE`): borra la membresía.
- Protección del último administrador y de la autogestión.
- Efecto inmediato en el acceso: las reglas de TK-017 ya exigen `approved`.
- Ocultación de los anuncios del miembro bloqueado (§3.4): amplía el filtro del listado (TK-028) y la visibilidad del detalle (TK-036).

**No incluye**
- Cambio de rol (`role`, p. ej. nombrar otro administrador o moderador): sin historia en el MVP; sigue respondiendo `422` (asumido).
- Salir de una comunidad por voluntad propia (`DELETE` sobre mí mismo): el contrato lo permite, pero no hay historia ni interfaz; se implementa la regla en la API por coherencia (§3.2) y queda sin pantalla.

## 3. Requisitos técnicos

### 3.1 Bloqueo (`PATCH` con `{"status": "blocked"}` o `{"status": "approved"}`)

- Solo `community_admin` de la comunidad o `platform_admin` (TK-017).
- Transiciones nuevas: `approved → blocked` (bloquear) y `blocked → approved` (desbloquear, asumido: permite corregir errores). Se actualizan `reviewed_by` y `reviewed_at`; `joined_at` se conserva.
- Un bloqueado no puede volver a solicitar el acceso (`409` de TK-015, con `status: blocked`).
- No se puede bloquear a un `community_admin` → **409** `{"detail": "No se puede bloquear a un administrador de la comunidad."}`.
- No me puedo bloquear a mí mismo → **409**.

### 3.2 Expulsión (`DELETE …/memberships/{user_id}`)

- Un `community_admin` puede eliminar la membresía de otros (en cualquier estado); cualquier usuario puede eliminar la suya.
- No se puede eliminar al **último** `community_admin` aprobado de la comunidad → **409** `{"detail": "La comunidad debe tener al menos un administrador."}`.
- Un administrador no puede expulsar a otro administrador (asumido) → **403**.
- Tras la expulsión, el usuario puede volver a solicitar el acceso (a diferencia del bloqueo) (asumido: expulsar es «sacar», bloquear es «impedir que vuelva»).
- **204**. **404** si la membresía no existe.
- Los anuncios del expulsado o bloqueado **no** se borran ni cambian de estado; dejan de poder editarse por él (TK-024 §3.1) y dejan de mostrarse (§3.4).

### 3.3 Listado (HU-16 AC1)

- `GET …/memberships` sin `status` ya devuelve todos los estados (TK-017). Se añade el orden por estado (`pending`, `approved`, `blocked`, `rejected`) y nombre cuando no se filtra (asumido), y el `role` en cada elemento (ya está en `Membership`).

### 3.4 Anuncios de miembros bloqueados

Al bloquear a un miembro, sus anuncios de esa comunidad quedan ocultos para el resto de miembros; al desbloquearlo vuelven a mostrarse tal como estaban.

- **Regla:** un anuncio solo es visible para los miembros si su autor tiene una membresía `approved` en la comunidad del anuncio. Se calcula al consultar, sin modificar `listing.status`: así no se mezcla con la retirada por moderación (`hidden`, TK-042) y el desbloqueo no necesita restaurar nada.
- **Listado y búsqueda** (TK-028, TK-030, TK-032, TK-034): el filtro común de `ListingQuery` añade `EXISTS (SELECT 1 FROM community_membership m WHERE m.community_id = listing.community_id AND m.user_id = listing.owner_id AND m.status = 'approved')`. Usa la PK `(community_id, user_id)`; `total` aplica el mismo filtro.
- **Detalle e imágenes** (TK-036, TK-021): `ListingVisibility` trata el anuncio de un autor sin membresía aprobada como `hidden`: lo ven los `community_admin`/`moderator` y `platform_admin` (para poder retirarlo, TK-042) y el resto recibe **404**. El autor bloqueado ya recibe **403** por no tener membresía aprobada.
- **Expulsión:** al borrar la membresía, la misma regla oculta también sus anuncios (asumido: el autor ya no pertenece a la comunidad); si vuelve a ser aprobado, se muestran de nuevo.
- La respuesta del `PATCH` de bloqueo no cambia; el frontend avisa de la ocultación en la confirmación (TK-041).

### 3.5 Pruebas

- Bloquear a un miembro → pierde el acceso al listado (**403** con `status: blocked`) y no puede publicar; desbloquear lo recupera.
- Bloquear a un miembro con anuncios → desaparecen del listado, de `q=…` y de `total` para otro miembro; su detalle da **404** a ese miembro y **200** al administrador; desbloquearlo los muestra de nuevo con su estado original (incluido `reserved`).
- Expulsar a un miembro con anuncios → dejan de mostrarse.
- Bloquear a un admin o a mí mismo → **409**.
- Expulsar → **204**; el expulsado recibe **403** sin membresía y puede volver a solicitar (**201**).
- Último administrador: no puede salir ni ser eliminado → **409**.
- Miembro sin rol → **403** en `PATCH` y `DELETE` sobre otros; sí puede eliminar su propia membresía (**204**).

## 4. Criterios de aceptación

**AC1 — Listado de miembros (HU-16 AC1)**
- **Given** que soy administrador de una comunidad
- **When** llamo a `GET …/memberships`
- **Then** recibo todos los miembros con su estado y su rol

**AC2 — Expulsar o bloquear (HU-16 AC2)**
- **Given** un miembro aprobado
- **When** lo bloqueo o lo expulso
- **Then** recibe `403` al ver el listado o publicar en la comunidad; si estaba bloqueado no puede volver a solicitar el acceso, y si fue expulsado sí

**AC3 — Anuncios ocultos al bloquear (HU-16 AC2)**
- **Given** un miembro aprobado con anuncios activos
- **When** lo bloqueo
- **Then** sus anuncios dejan de aparecer en el listado, en las búsquedas y en el detalle para los demás miembros; al desbloquearlo vuelven a aparecer

**AC4 — Restricción a administradores (HU-16 AC3)**
- **Given** que soy miembro sin rol de administrador
- **When** intento bloquear o expulsar a otro miembro
- **Then** recibo `403` y no cambia nada

**AC5 — Protecciones**
- **Given** una comunidad con un único administrador
- **When** se intenta eliminar su membresía o bloquearlo
- **Then** se responde `409` y la comunidad conserva su administrador

## 5. Plan de tareas

1. Transiciones de bloqueo y desbloqueo con sus protecciones.
2. Caso de uso `RemoveMembership` (expulsión y salida) con la regla del último administrador.
3. Ocultación de anuncios de autores sin membresía aprobada (filtro de `ListingQuery` y `ListingVisibility`).
4. Orden del listado completo.
5. Pruebas de §3.5; verificación según la sección 6.

## 6. Verificación

```bash
curl -s -X PATCH http://localhost:8000/v1/communities/<id>/memberships/<user> -H "Authorization: Bearer $ADMIN" \
  -H 'Content-Type: application/json' -d '{"status":"blocked"}'
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost:8000/v1/communities/<id>/listings" -H "Authorization: Bearer $BLOQUEADO"  # 403
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE http://localhost:8000/v1/communities/<id>/memberships/<otro> -H "Authorization: Bearer $ADMIN"  # 204
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Expulsar frente a bloquear:** la diferencia (poder volver a solicitar o no) es una propuesta; confirmar con negocio.
- **Coste del filtro de autor:** un `EXISTS` por la PK de `community_membership`; despreciable con el volumen del MVP.
