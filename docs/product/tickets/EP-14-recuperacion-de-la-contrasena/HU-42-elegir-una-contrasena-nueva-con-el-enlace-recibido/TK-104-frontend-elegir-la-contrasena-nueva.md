# TK-104 · Frontend: elegir la contraseña nueva desde el enlace del correo

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/auth`, `/restablecer-contrasena`, `/restablecer-contrasena/enlace`, `/iniciar-sesion`) |
| **Historia** | HU-42 Elegir una contraseña nueva con el enlace recibido (Épica 14) |
| **Prioridad** | Alta |
| **Depende de** | TK-060, TK-102, TK-103 |
| **Referencias** | `app/verificar-correo/route.ts` (*route handler* con el *token*); `app/iniciar-sesion/page.tsx` (`NOTICES`); `features/auth/schemas.ts` (reglas de la contraseña) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El correo de TK-101 lleva a `/restablecer-contrasena/enlace?token=…`. TK-102 expone `POST /v1/auth/password-reset/confirm`.

**Objetivo:** recibir el enlace sin dejar el *token* en la barra de direcciones, pedir la contraseña nueva dos veces, cambiarla y llevar al inicio de sesión con un aviso; si el enlace no vale, explicarlo y ofrecer pedir otro.

## 2. Alcance

**Incluye**
- *Route handler* `/restablecer-contrasena/enlace`.
- Página `/restablecer-contrasena` con su formulario y Server Action `resetPassword`.
- Página de enlace no válido o caducado.
- Avisos nuevos en `/iniciar-sesion`.
- Rutas en `PUBLIC_ROUTES`.

**No incluye**
- El cambio de contraseña desde el perfil.

## 3. Requisitos técnicos

### 3.1 `/restablecer-contrasena/enlace` (`GET`, *route handler*)

- Sin `token` → `/restablecer-contrasena?motivo=invalido`.
- Con `token` → guarda el *token* en la *cookie* `ev_password_reset` (`HttpOnly`, `Secure` fuera de desarrollo, `SameSite=Lax`, `Path=/restablecer-contrasena`, `Max-Age` 3600) y redirige a `/restablecer-contrasena`, sin el *token* en la URL (asumido: así no queda en el historial ni en la cabecera `Referer`).
- No llama a la API: un escáner de enlaces que abra el correo no consume nada.
- Respuesta con `Referrer-Policy: no-referrer` y `Cache-Control: no-store`, como `/verificar-correo`.

### 3.2 `/restablecer-contrasena`

- Sin *cookie* o con `motivo=invalido|caducado` → mensaje y enlace «Pedir otro enlace» a `/recuperar-contrasena` (HU-42 AC2):
  - `invalido`: «El enlace para restablecer la contraseña no es válido. Puede que ya lo hayas usado o que hayas pedido otro más reciente.».
  - `caducado`: «El enlace para restablecer la contraseña ha caducado.».
- Con *cookie* → formulario con «Contraseña nueva» y «Repite la contraseña» (`autocomplete="new-password"`), las mismas reglas que el registro (12 a 128 caracteres) y error si no coinciden. Botón «Cambiar contraseña».
- Server Action `resetPassword` (lee el *token* de la *cookie*, nunca de un campo del formulario):
  - `204` → borra la *cookie* y la de sesión si existiera, y redirige a `/iniciar-sesion?motivo=contrasena-cambiada`.
  - `410` → borra la *cookie* y muestra el mensaje de caducado.
  - `400` → borra la *cookie* y muestra el mensaje de no válido.
  - `422` → errores junto a los campos, sin borrar la *cookie*.
  - Red o `5xx` → «No hemos podido cambiar la contraseña. Inténtalo de nuevo en unos minutos.».
- `metadata.title`: «Nueva contraseña · EntreVecinos».

### 3.3 Inicio de sesión

- `NOTICES["contrasena-cambiada"]`: «Tu contraseña se ha cambiado. Inicia sesión con la nueva.» (HU-42 AC1).

### 3.4 Pruebas

- *Route handler*: con y sin *token*; *cookie* con sus atributos; cabeceras.
- `resetPassword`: `204`, `410`, `400`, `422`, error de red; contraseñas que no coinciden no llaman a la API.
- Página: formulario con *cookie*, mensajes sin ella.
- Inicio de sesión: aviso `contrasena-cambiada`.

## 4. Criterios de aceptación

**AC1 — Contraseña cambiada (HU-42 AC1)**
- **Given** el enlace del correo en Mailpit
- **When** lo abre, escribe dos veces una contraseña válida y la envía
- **Then** llega a `/iniciar-sesion` con «Tu contraseña se ha cambiado. Inicia sesión con la nueva.» y puede entrar con ella

**AC2 — Token fuera de la URL**
- **Given** que abre el enlace del correo
- **When** se muestra el formulario
- **Then** la barra de direcciones muestra `/restablecer-contrasena` sin el *token*

**AC3 — Enlace no válido (HU-42 AC2)**
- **Given** un enlace caducado, usado o sustituido
- **When** lo abre y envía el formulario
- **Then** ve el mensaje correspondiente y el enlace «Pedir otro enlace»

**AC4 — Sesión cerrada (HU-42 AC3)**
- **Given** una sesión abierta en otro navegador
- **When** cambia la contraseña
- **Then** en ese navegador, la siguiente página privada lleva a `/iniciar-sesion?motivo=sesion-caducada`

## 5. Plan de tareas

1. *Route handler* `/restablecer-contrasena/enlace`.
2. Server Action `resetPassword` y esquema zod con confirmación.
3. Página `/restablecer-contrasena`, mensajes y rutas públicas.
4. Aviso en `/iniciar-sesion`.
5. Pruebas.
6. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
# Pedir el enlace en http://localhost:3000/recuperar-contrasena, abrirlo desde http://localhost:8025,
# cambiar la contraseña y entrar con la nueva; repetir el enlace → «no es válido».
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] Lint, tipos y pruebas de la web pasan.
- [ ] Recorrido completo comprobado en local y en producción.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Enlace abierto en otro navegador:** la *cookie* vive en el navegador que abrió el enlace; si se copia la página sin el enlace, no hay formulario. Es lo esperado: hay que abrir el enlace del correo.
- **CSP:** las páginas nuevas no añaden orígenes externos ni *scripts* en línea; la `Content-Security-Policy` no cambia.
