# TK-055 · Frontend: cerrar sesión desde la cabecera

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/auth`, cabecera de la zona privada) |
| **Historia** | HU-24 Cerrar sesión (Épica 9) |
| **Prioridad** | Alta |
| **Depende de** | TK-009, TK-047 |
| **Referencias** | `user-stories.md` HU-24 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La sesión es un JWT guardado en la *cookie* `httpOnly` `ev_session` (TK-009). No hay forma de cerrarla: el usuario tiene que esperar a que caduque o borrar las *cookies* a mano, un problema en equipos compartidos.

**Objetivo:** un botón «Cerrar sesión» en la cabecera de la zona privada que borra la sesión y lleva a la raíz del sitio.

## 2. Alcance

**Incluye**
- *Server Action* `logout()` que borra la *cookie* `ev_session` y redirige a `/`.
- Botón «Cerrar sesión» al final de la navegación de la cabecera privada, junto a «Mi perfil».

**No incluye**
- Revocar el token en la API: el JWT no tiene estado y la API no tiene endpoint de cierre de sesión (asumido). Al borrar la *cookie*, el navegador deja de tenerlo; un token copiado antes seguiría siendo válido hasta caducar.
- Confirmación antes de cerrar: cerrar sesión no destruye datos y la práctica habitual es hacerlo con un clic (asumido).

## 3. Requisitos técnicos

### 3.1 *Server Action* `logout`

- `deleteSession()` en `features/auth/session.ts` borra `ev_session` (mismo `path` con el que se creó).
- `logout()` en `features/auth/actions.ts`: `deleteSession()` y `redirect("/")`. La raíz redirige a `/iniciar-sesion` sin sesión (TK-047).
- Borrar una *cookie* en una *Server Action* invalida la caché del router del cliente, así que «Atrás» no muestra páginas privadas ya visitadas.
- Se envía con un formulario `POST`: un enlace `GET` permitiría cerrar la sesión desde otra web o con un *prefetch*. Las *Server Actions* comprueban el origen de la petición.

### 3.2 Cabecera

- En `app/(privado)/layout.tsx`, último elemento de la navegación: `<form action={logout}>` con un `<button type="submit">` «Cerrar sesión», con el mismo estilo que los enlaces de la navegación para no competir con las acciones principales.
- Es un botón, no un enlace (cambia el estado); accesible con teclado y lector de pantalla sin atributos adicionales.
- En pantallas estrechas la navegación ya se ajusta en varias líneas (`flex-wrap`).

### 3.3 Pruebas

- `logout`: borra la *cookie* `ev_session` y redirige a `/`.

## 4. Criterios de aceptación

**AC1 — Acceso visible (HU-24 AC1)**
- **Given** un vecino con sesión
- **When** abre cualquier página privada
- **Then** ve «Cerrar sesión» en la cabecera, después de «Mi perfil»

**AC2 — Cierre de sesión (HU-24 AC2)**
- **Given** un vecino con sesión
- **When** pulsa «Cerrar sesión»
- **Then** la *cookie* `ev_session` desaparece y acaba en `/iniciar-sesion`, pasando por `/`

**AC3 — Sin acceso tras cerrar (HU-24 AC3)**
- **Given** que ha cerrado la sesión
- **When** abre `/inicio` o pulsa «Atrás»
- **Then** se le redirige a `/iniciar-sesion`

## 5. Plan de tareas

1. `deleteSession` y *Server Action* `logout` con prueba.
2. Botón en la cabecera privada.
3. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Iniciar sesión → «Cerrar sesión» en la cabecera → /iniciar-sesion, sin cookie ev_session
# Atrás o /inicio → /iniciar-sesion?next=...
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Sin revocación en el servidor:** un token robado antes del cierre sigue sirviendo hasta que caduca. Revocarlo necesitaría una lista de tokens invalidados o tokens de corta duración con renovación.
