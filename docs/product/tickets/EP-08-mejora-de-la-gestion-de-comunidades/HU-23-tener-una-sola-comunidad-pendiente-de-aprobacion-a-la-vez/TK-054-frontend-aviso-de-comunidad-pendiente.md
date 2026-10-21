# TK-054 · Frontend: aviso de comunidad pendiente al crear una comunidad

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`/comunidades/nueva`, `createCommunity`) |
| **Historia** | HU-23 Tener una sola comunidad pendiente de aprobación a la vez (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-051, TK-053 |
| **Referencias** | `user-stories.md` HU-23 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-053, la API rechaza con `409` una segunda comunidad pendiente. Hoy la web mostraría el error genérico tras rellenar el formulario.

**Objetivo:** avisar antes de rellenar el formulario y traducir el `409` si llega igualmente.

## 2. Alcance

**Incluye**
- `/comunidades/nueva`: aviso en lugar del formulario si el usuario ya tiene una comunidad pendiente.
- `createCommunity`: mensaje propio para el `409`.

**No incluye**
- Ocultar los enlaces a «Crear una comunidad» de otras páginas: llevan a la página, que explica la situación (asumido).

## 3. Requisitos técnicos

### 3.1 Página

- Con `getMyMemberships()`, la comunidad pendiente es la que tiene `community.is_active === false` y `community.created_by === user.id`.
- Si existe: aviso `role="status"` «Ya tienes una comunidad pendiente de aprobación: «{nombre}». Podrás crear otra cuando un administrador la revise.», enlace «Volver al inicio» y sin formulario.

### 3.2 *Server Action*

- `409` → `formError` «Ya tienes una comunidad pendiente de aprobación.», conservando los valores.

### 3.3 Pruebas

- `createCommunity`: `409` → mensaje propio.
- Función que encuentra la comunidad pendiente del usuario: sin membresías, pendiente propia, inactiva de otro creador, activa.

## 4. Criterios de aceptación

**AC1 — Aviso (HU-23 AC1)**
- **Given** un vecino con una comunidad pendiente
- **When** abre `/comunidades/nueva`
- **Then** ve el aviso con el nombre de su comunidad pendiente y no ve el formulario

**AC2 — Tras la aprobación (HU-23 AC2)**
- **Given** que su comunidad se ha aprobado
- **When** abre `/comunidades/nueva`
- **Then** ve el formulario y puede crear otra comunidad

**AC3 — Conflicto**
- **Given** que la API responde `409` al crear (por ejemplo, desde otra pestaña)
- **When** el vecino envía el formulario
- **Then** ve «Ya tienes una comunidad pendiente de aprobación.» y conserva lo escrito

## 5. Plan de tareas

1. `pendingCommunityOf(memberships, userId)` con pruebas.
2. Aviso en `/comunidades/nueva`.
3. `409` en `createCommunity` con prueba.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Vecino: crear una comunidad → /comunidades/nueva muestra el aviso
# platform_admin la aprueba → /comunidades/nueva vuelve a mostrar el formulario
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- Ninguno relevante.
