# TK-057 · BD: correo validado y tokens de validación (migración `0008`)

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos |
| **Componente** | `apps/api/` (migración `0008`, modelos) |
| **Historia** | HU-25 Validar mi correo electrónico al registrarme (Épica 10) |
| **Prioridad** | Alta |
| **Depende de** | TK-005 |
| **Referencias** | `readme.md` (modelo de datos, tabla `user`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Hay que saber si el correo de cada cuenta está validado y guardar los enlaces de validación con su caducidad, sin que una copia de la base de datos permita usarlos.

**Objetivo:** añadir la fecha de validación a `users`, la tabla `email_verification` y una restricción que impida tener activa una cuenta sin validar, salvo la de un `platform_admin`.

## 2. Alcance

**Incluye**
- Columna `users.email_verified_at TIMESTAMPTZ NULL`.
- Tabla `email_verification`.
- `CHECK` sobre `users`.
- *Backfill* de las cuentas existentes.

**No incluye**
- La lógica de registro, validación y reenvío (TK-058, TK-059).

## 3. Requisitos técnicos

### 3.1 `users`

- `email_verified_at TIMESTAMPTZ NULL`.
- *Backfill*: `email_verified_at = created_at` para las cuentas que ya existen (asumido: hasta ahora todas se activaban al registrarse, y obligarlas a validar dejaría fuera a los usuarios actuales).
- `CHECK (NOT is_active OR email_verified_at IS NOT NULL OR platform_role = 'platform_admin')`, nombre `ck_users_active_requires_verified_email`. La base de datos garantiza así la regla de HU-25.
- `is_active` mantiene `DEFAULT true`; el registro inserta `false` de forma explícita (TK-058).

### 3.2 `email_verification`

| Columna | Tipo | Notas |
|---|---|---|
| `token_hash` | `CHAR(64)` | **PK**. SHA-256 en hexadecimal del token; el token en claro solo viaja en el correo |
| `user_id` | `UUID` | `NOT NULL`, **FK** → `users.id` `ON DELETE CASCADE` |
| `expires_at` | `TIMESTAMPTZ` | `NOT NULL` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT now()` |

- Índice por `user_id` (el reenvío borra los tokens anteriores del usuario).
- Un token usado se borra; no hace falta `used_at` (asumido).

### 3.3 Migración

- `0008`, reversible: `downgrade` elimina la tabla, la restricción y la columna.

### 3.4 Pruebas

- La restricción rechaza una cuenta activa sin validar con rol `user` y la admite con `platform_admin`.
- *Backfill*: tras la migración, las cuentas existentes tienen `email_verified_at`.
- Borrar un usuario borra sus tokens.
- Migración reversible.

## 4. Criterios de aceptación

**AC1 — Cuenta activa sin validar**
- **Given** una cuenta `user` con `email_verified_at` nulo
- **When** se intenta guardar con `is_active = true`
- **Then** falla la restricción `ck_users_active_requires_verified_email`

**AC2 — Administrador de plataforma**
- **Given** una cuenta `platform_admin` sin validar
- **When** se guarda con `is_active = true`
- **Then** se acepta

**AC3 — Cuentas existentes**
- **Given** una base de datos con usuarios anteriores a la migración
- **When** se aplica `0008`
- **Then** todos siguen activos y con `email_verified_at` informado

## 5. Plan de tareas

1. Migración `0008` y modelos (`UserModel.email_verified_at`, `EmailVerificationModel`).
2. Pruebas de restricción, *backfill*, cascada y reversibilidad.
3. Verificación según la sección 6.

## 6. Verificación

```bash
make migrate
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q -m db
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] La migración se aplica y se revierte.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Nombrar un `platform_admin` a mano** (`UPDATE users SET platform_role = ...`) sigue funcionando aunque no haya validado su correo.
