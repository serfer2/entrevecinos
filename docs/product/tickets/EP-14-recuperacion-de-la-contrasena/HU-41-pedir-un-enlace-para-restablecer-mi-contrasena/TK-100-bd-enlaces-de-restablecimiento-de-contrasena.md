# TK-100 · BD: enlaces de restablecimiento de contraseña y fecha del último cambio (migración `0011`)

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos |
| **Componente** | `apps/api/` (migración `0011`, modelos), `readme.md` (§3.1 y §3.2) |
| **Historia** | HU-41 Pedir un enlace para restablecer mi contraseña (Épica 14); también sirve a HU-42 |
| **Prioridad** | Alta |
| **Depende de** | TK-057, TK-063, TK-099 (migración `0010`) |
| **Referencias** | TK-057 (tabla `email_verification`, mismo esquema de *token* con hash); `readme.md` §3.2 (`user`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Para restablecer una contraseña hay que guardar los enlaces enviados por correo con su caducidad, sin que una copia de la base de datos permita usarlos, y saber cuándo cambió la contraseña de cada cuenta para invalidar las sesiones anteriores (HU-42 AC3).

**Objetivo:** añadir la tabla `password_reset` y la columna `users.password_changed_at`, y documentarlas como parte del MVP en el modelo de datos.

## 2. Alcance

**Incluye**
- Tabla `password_reset`.
- Columna `users.password_changed_at`.
- Modelos SQLAlchemy y migración `0011` reversible.
- Diagrama y descripción del modelo en `readme.md` (§3.1 y §3.2), con la entidad marcada como MVP.

**No incluye**
- La lógica de solicitud y de cambio de contraseña (TK-101, TK-102).
- Limpieza periódica de enlaces caducados (asumido: se borran al pedir otro o al usarlo, como en TK-057).

## 3. Requisitos técnicos

### 3.1 `password_reset`

| Columna | Tipo | Notas |
|---|---|---|
| `token_hash` | `CHAR(64)` | **PK**. SHA-256 en hexadecimal del *token*; el *token* en claro solo viaja en el correo |
| `user_id` | `UUID` | `NOT NULL`, **FK** → `users.id` `ON DELETE CASCADE` |
| `expires_at` | `TIMESTAMPTZ` | `NOT NULL` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` |

- Índice por `user_id`: pedir un enlace nuevo borra los anteriores del usuario y el límite de uno por minuto consulta el más reciente.
- Un enlace usado o sustituido se borra. A diferencia de la validación del correo (TK-063), la web no necesita distinguir por qué un enlace no vale: a quien lo abre le basta con pedir otro (asumido).

### 3.2 `users.password_changed_at`

- `TIMESTAMPTZ NULL`. `NULL` en las cuentas existentes: nunca han cambiado la contraseña desde que existe la columna, así que sus sesiones siguen valiendo.
- La API rechazará los JWT emitidos antes de esta fecha (TK-102).

### 3.3 Migración

- `0011`, reversible: `downgrade` elimina la tabla y la columna.

### 3.4 Documentación

- `readme.md` §3.1: entidad `password_reset` en el diagrama y columna `password_changed_at` en `user`.
- `readme.md` §3.2: descripción de `password_reset` con alcance **MVP** y las operaciones que la usan (`POST /auth/password-reset`, `POST /auth/password-reset/confirm`).

### 3.5 Pruebas

- Borrar un usuario borra sus enlaces.
- La migración sube y baja sin errores; `alembic check` no encuentra diferencias con los modelos.

## 4. Criterios de aceptación

**AC1 — Enlaces guardados con hash**
- **Given** la migración `0011` aplicada
- **When** se inspecciona `password_reset`
- **Then** guarda solo el hash del *token*, su usuario y su caducidad, y un usuario borrado no deja enlaces

**AC2 — Cuentas existentes intactas**
- **Given** una base de datos con usuarios anteriores a la migración
- **When** se aplica `0011`
- **Then** todos conservan su contraseña y sus sesiones, con `password_changed_at` nulo

**AC3 — Reversible**
- **Given** la migración `0011` aplicada
- **When** se ejecuta `alembic downgrade -1`
- **Then** desaparecen la tabla y la columna sin afectar al resto

**AC4 — Documentado como MVP**
- **Given** el `readme.md`
- **When** consulto el modelo de datos
- **Then** encuentro `password_reset` en el diagrama y en la tabla de alcance como entidad del MVP

## 5. Plan de tareas

1. Modelos `PasswordResetModel` y columna en `UserModel`.
2. Migración `0011` revisada a mano, con `downgrade()`.
3. Pruebas de la migración y del borrado en cascada.
4. Diagrama y descripción en `readme.md`.
5. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api alembic downgrade -1 && $COMPOSE run --rm api alembic upgrade head
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Las pruebas de la API y `ruff` pasan; `alembic check` sin diferencias.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Producción:** `deploy.sh` hace una copia de la base antes de aplicar `0011` (TK-092). La migración solo añade objetos, así que es segura con la API anterior en marcha.
