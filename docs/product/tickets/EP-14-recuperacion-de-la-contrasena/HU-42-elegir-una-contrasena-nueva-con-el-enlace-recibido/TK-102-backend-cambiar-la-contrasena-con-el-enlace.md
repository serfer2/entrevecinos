# TK-102 · Backend: cambiar la contraseña con el enlace y cerrar las sesiones anteriores (`POST /v1/auth/password-reset/confirm`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `users`, seguridad, correo), `docs/api/` |
| **Historia** | HU-42 Elegir una contraseña nueva con el enlace recibido (Épica 14) |
| **Prioridad** | Alta |
| **Depende de** | TK-100, TK-101 |
| **Referencias** | `application/users/verify_email.py`; `infrastructure/security/jwt_tokens.py` (`iat`); `application/users/get_current_user.py`; `ports.py` (`update_password_hash`, `mark_email_verified`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-101, el vecino recibe un enlace de un solo uso. Falta el paso que cambia la contraseña. Además, los JWT duran 24 horas y no se pueden revocar: si alguien conocía la contraseña antigua y tiene una sesión abierta, debe perderla al cambiarla.

**Objetivo:** un endpoint público que, con un enlace válido y una contraseña nueva, cambia la contraseña, invalida el enlace, cierra todas las sesiones anteriores y avisa por correo.

## 2. Alcance

**Incluye**
- Caso de uso `ResetPassword`.
- Endpoint `POST /v1/auth/password-reset/confirm`.
- Rechazo de los JWT emitidos antes de `password_changed_at` en `GetCurrentUser`.
- Correo de aviso del cambio.
- Contrato (`x-mvp: true`) y tabla de cambios de `docs/api/README.md`; extracto del `readme.md` y §2.5 (Seguridad).

**No incluye**
- La interfaz (TK-104).
- Cambiar la contraseña desde el perfil conociendo la actual (fuera de esta épica).

## 3. Requisitos técnicos

### 3.1 `POST /v1/auth/password-reset/confirm`

- Público (`security: []`). Cuerpo `{"token": "...", "password": "..."}` (`extra="forbid"`); `password` con las mismas reglas que el registro (12 a 128 caracteres).
- Enlace válido y sin caducar → `204`. **No inicia la sesión** (asumido): la web lleva al inicio de sesión, así quien abre el enlace demuestra también que recuerda la contraseña nueva.
- Enlace caducado → `410` `{"detail": "El enlace para restablecer la contraseña ha caducado.", "code": "password_reset_expired"}`.
- Enlace desconocido, usado o sustituido → `400` `{"detail": "El enlace para restablecer la contraseña no es válido.", "code": "password_reset_invalid"}`.
- Contraseña que no cumple las reglas → `422`, sin consumir el enlace.
- Esquemas nuevos `PasswordResetConfirmRequest` y `PasswordResetError` (`Error` + `code`).

### 3.2 `ResetPassword`

En una transacción:
1. Busca el enlace por `hash_token(token)`; comprueba la caducidad con el reloj inyectado.
2. Vuelve a comprobar la cuenta (no borrada ni desactivada con el correo validado); si ya no puede usarse, `400` como enlace no válido.
3. `change_password` con Argon2 y `password_changed_at = statement_timestamp()` (no `update_password_hash`, que solo reescribe el hash al iniciar sesión y no debe cerrar sesiones).
4. Si el correo estaba sin validar, `mark_email_verified` (HU-42 AC5).
5. Borra todos los enlaces de restablecimiento del usuario.

### 3.3 Sesiones anteriores (HU-42 AC3)

- `JwtTokenService.decode` devuelve también `iat`.
- `GetCurrentUser` rechaza con `NotAuthenticated` (`401`) un *token* con `iat` anterior a `password_changed_at`. Como `iat` va en segundos enteros, se compara con `password_changed_at` truncado al segundo: los *tokens* emitidos en el mismo segundo del cambio siguen valiendo (asumido; ningún *token* se emite en ese segundo porque el endpoint no inicia sesión).
- La web ya trata el `401` como sesión caducada (TK-009) y lleva al inicio de sesión.

### 3.4 Aviso por correo (HU-42 AC4)

- Tras confirmar la transacción, en segundo plano: asunto «Tu contraseña de EntreVecinos ha cambiado», con la fecha y hora (Europe/Madrid) y «Si no has sido tú, pide un enlace nuevo desde "¿Has olvidado tu contraseña?" y avisa a la administración de tu comunidad.».
- Consume una plaza del cupo. Si no queda cupo, **la contraseña cambia igual** y el aviso no se envía; se registra el bloqueo como en TK-099 (asumido: el cambio pedido por el usuario prima sobre el aviso).

### 3.5 Pruebas

- Enlace válido: `204`, la contraseña nueva inicia sesión, la antigua no, el enlace deja de valer y llega el aviso.
- Caducado (`410`), usado (`400`), sustituido por uno más reciente (`400`), inventado (`400`).
- Contraseña corta: `422` y el enlace sigue valiendo.
- Cuenta sin validar: tras el cambio queda validada y activa.
- Sesión anterior: un JWT emitido antes del cambio recibe `401` en `GET /users/me`; uno emitido después, `200`.
- Sin cupo: `204`, contraseña cambiada y ningún aviso.

## 4. Criterios de aceptación

**AC1 — Cambio de contraseña (HU-42 AC1)**
- **Given** un enlace emitido hace menos de 60 minutos
- **When** se hace `POST /v1/auth/password-reset/confirm` con una contraseña válida
- **Then** se recibe `204`, la nueva contraseña inicia sesión, la antigua no y el enlace deja de valer

**AC2 — Enlace no válido (HU-42 AC2)**
- **Given** un enlace caducado, usado o sustituido
- **When** se confirma
- **Then** se recibe `410` (caducado) o `400` (resto) y la contraseña no cambia

**AC3 — Sesiones cerradas (HU-42 AC3)**
- **Given** un JWT emitido antes del cambio
- **When** se usa después
- **Then** la API responde `401`

**AC4 — Aviso (HU-42 AC4)**
- **Given** un cambio de contraseña correcto
- **When** reviso Mailpit
- **Then** hay un correo que avisa del cambio

**AC5 — Cuenta sin validar (HU-42 AC5)**
- **Given** una cuenta con el correo sin validar
- **When** cambia la contraseña con el enlace
- **Then** queda validada y puede iniciar sesión

## 5. Plan de tareas

1. `iat` en `JwtTokenService.decode` y regla en `GetCurrentUser`.
2. `ResetPassword` y plantilla del aviso.
3. Endpoint, errores y esquemas.
4. Contrato, `docs/api/README.md`, extracto y §2.5 del `readme.md`.
5. Pruebas.
6. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# 1. POST /v1/auth/password-reset y copiar el token del correo en http://localhost:8025
# 2. POST /v1/auth/password-reset/confirm {"token": "...", "password": "..."} → 204
# 3. GET /v1/users/me con el JWT anterior → 401; POST /v1/auth/token con la nueva → 200
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Contrato y `readme.md` (§2.5 y extracto de la API) actualizados.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Consulta extra por petición:** `GetCurrentUser` ya carga el usuario en cada petición autenticada, así que comparar `password_changed_at` no añade consultas.
- **Escáneres de enlaces:** el enlace del correo solo abre una página (TK-104); cambiar la contraseña exige enviar un formulario, así que un escáner no puede consumir el enlace.
- **Cambio de contraseña desde el perfil:** queda como mejora posterior; usaría también `password_changed_at`.
