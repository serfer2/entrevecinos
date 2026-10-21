# TK-065 · Frontend: mensaje del enlace de validación sustituido o no válido

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`app/verificar-correo`, `/verificar-correo/error`), `apps/web/README.md` |
| **Historia** | HU-27 Entender por qué no funciona un enlace de validación antiguo (Épica 10) |
| **Prioridad** | Media |
| **Depende de** | TK-060, TK-061, TK-064 |
| **Referencias** | `apps/web/src/app/verificar-correo/route.ts`; TK-060 §3.2 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El *route handler* `/verificar-correo` trata cualquier `400` igual: con sesión lleva a `/comunidades` y sin ella a `/iniciar-sesion?motivo=correo-validado` («Tu correo ya está validado. Inicia sesión.»). Con un enlace sustituido por un reenvío, el mensaje es falso: la cuenta sigue pendiente. TK-064 añade el motivo en `code`.

**Objetivo:** mostrar el mensaje que corresponde a cada motivo y ofrecer el reenvío cuando el enlace se ha sustituido.

## 2. Alcance

**Incluye**
- `/verificar-correo`: redirección según el `code` del `400`.
- `/verificar-correo/error`: motivo nuevo `reemplazado`.
- `apps/web/README.md` (flujo de validación).

**No incluye**
- Cambios en el registro o en el inicio de sesión.

## 3. Requisitos técnicos

### 3.1 `/verificar-correo` (`400`)

| `code` | Destino |
|---|---|
| `email_already_verified` | Con sesión válida, `/comunidades`; sin ella, `/iniciar-sesion?motivo=correo-validado` (comportamiento actual) |
| `verification_superseded` | `/verificar-correo/error?motivo=reemplazado&email=<correo>` |
| `verification_invalid` o cualquier otro | `/verificar-correo/error?motivo=invalido` |

- Se lee con `errorCodeOf` (`lib/api/errors.ts`). Las cabeceras (`303`, `Location` relativo, `Cache-Control: no-store`, `Referrer-Policy: no-referrer`) no cambian.

### 3.2 `/verificar-correo/error?motivo=reemplazado`

- Alerta: «Este enlace ya no es válido porque te hemos enviado uno más reciente. Abre el enlace del último correo que has recibido.».
- Con `email` en la URL, `ResendVerificationButton` (TK-061); sin él, enlace a `/registro`, igual que `caducado`.
- `invalido` y `error` sin cambios; un `motivo` desconocido sigue mostrando `invalido`.

### 3.3 Pruebas

- *Route handler*: `400` con cada `code`, con y sin sesión en `email_already_verified`; `400` sin `code` → `invalido`.
- Página de error: `reemplazado` con y sin `email`.

## 4. Criterios de aceptación

**AC1 — Enlace sustituido (HU-27 AC1)**
- **Given** una cuenta pendiente que ha pedido un reenvío, sin sesión
- **When** abre el enlace del primer correo
- **Then** ve «Este enlace ya no es válido porque te hemos enviado uno más reciente…» y el botón «Reenviar el correo de validación», y no «Tu correo ya está validado»

**AC2 — Cuenta ya validada (HU-27 AC2)**
- **Given** una cuenta validada, sin sesión
- **When** abre de nuevo su enlace
- **Then** llega a `/iniciar-sesion` con «Tu correo ya está validado. Inicia sesión.»

**AC3 — Enlace desconocido (HU-27 AC3)**
- **Given** un enlace con un token inventado
- **When** lo abre
- **Then** ve «El enlace de validación no es válido.»

## 5. Plan de tareas

1. Redirección por `code` en el *route handler*, con pruebas.
2. Motivo `reemplazado` en la página de error, con pruebas.
3. `apps/web/README.md`.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Registrar un correo, esperar 60 s y pedir el reenvío desde /iniciar-sesion
# Abrir en Mailpit (http://localhost:8025) el enlace del primer correo → mensaje de enlace sustituido + botón
# Abrir el del segundo → /comunidades; cerrar sesión y abrirlo otra vez → «Tu correo ya está validado»
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Correo en la URL:** igual que en `caducado` (TK-060 §8).
