# TK-063 · BD: conservar los enlaces de validación usados y sustituidos (migración `0009`)

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos |
| **Componente** | `apps/api/` (migración `0009`, modelos, repositorio), `readme.md` (modelo de datos) |
| **Historia** | HU-27 Entender por qué no funciona un enlace de validación antiguo (Épica 10) |
| **Prioridad** | Media |
| **Depende de** | TK-057, TK-059 |
| **Referencias** | `readme.md` §3.2 `email_verification`; TK-058 §3.2 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Hoy, emitir un enlace nuevo borra los anteriores del usuario (TK-058 §3.2) y validar el correo borra todos los suyos. Por eso, cuando llega un token antiguo la API solo puede decir «no existe» (`400 verification_invalid`), sin distinguir un enlace sustituido de uno ya usado o de uno que nunca se envió. La web interpreta ese `400`, sin sesión, como «Tu correo ya está validado» (TK-060 §3.2), lo que es falso si la cuenta sigue pendiente.

**Objetivo:** conservar los enlaces usados y sustituidos, marcados como tales, para que la API sepa el motivo por el que un token ya no vale.

## 2. Alcance

**Incluye**
- Columnas `used_at` y `superseded_at` en `email_verification`.
- Repositorio: marcar en lugar de borrar.
- Purga de enlaces antiguos.
- Modelo de datos de `readme.md`.

**No incluye**
- Las respuestas de la API (TK-064) ni los mensajes de la web (TK-065).

## 3. Requisitos técnicos

### 3.1 `email_verification`

| Columna | Tipo | Notas |
|---|---|---|
| `used_at` | `TIMESTAMPTZ` | `NULL`; fecha en que se validó el correo con este enlace |
| `superseded_at` | `TIMESTAMPTZ` | `NULL`; fecha en que otro enlace más reciente lo sustituyó |

- `CHECK (used_at IS NULL OR superseded_at IS NULL)`, nombre `ck_email_verification_used_or_superseded`: un enlace no puede estar en los dos estados.
- Índice parcial único `uq_email_verification_one_active_per_user` sobre `user_id` `WHERE used_at IS NULL AND superseded_at IS NULL`: como mucho un enlace vigente por usuario, también con peticiones concurrentes (asumido).
- El token sigue guardándose solo como SHA-256 (`token_hash`).

### 3.2 Repositorio (`EmailVerificationRepository`)

- `replace(user_id, token_hash, expires_at)`: marca `superseded_at = now()` en los enlaces vigentes del usuario e inserta el nuevo. Ya no borra.
- `get(token_hash)`: devuelve también `used_at` y `superseded_at` (`EmailVerification`).
- `mark_used(token_hash)`: `used_at = now()` en ese enlace y `superseded_at = now()` en el resto de vigentes del usuario. Sustituye a `delete_for_user` en `VerifyEmail`.
- `last_created_at(user_id)`: sin cambios (el límite de 60 segundos de TK-059 cuenta cualquier enlace).

### 3.3 Purga

- Al emitir un enlace, se borran los del mismo usuario con `expires_at` anterior a hace 30 días (asumido: un enlace con más de un mes no se va a abrir y la tabla no crece sin límite). Los demás se borran en cascada con el usuario.
- Un token purgado vuelve a ser desconocido (`verification_invalid`, TK-064).

### 3.4 Migración

- `0009`, reversible. `upgrade`: añade las columnas, la restricción y el índice. Los enlaces existentes quedan vigentes (columnas nulas); como hasta ahora se borraban al sustituirlos, hay como mucho uno por usuario y el índice único se crea sin conflictos. `downgrade`: borra las filas usadas o sustituidas y elimina índice, restricción y columnas.

### 3.5 Pruebas

- Restricción: un enlace con `used_at` y `superseded_at` a la vez se rechaza.
- Índice: no se pueden insertar dos enlaces vigentes del mismo usuario.
- `replace` marca el anterior como sustituido; `mark_used` marca el usado y sustituye el resto.
- Purga de enlaces caducados hace más de 30 días.
- Migración reversible.

## 4. Criterios de aceptación

**AC1 — Enlace sustituido**
- **Given** un usuario con un enlace vigente
- **When** se le emite otro
- **Then** el anterior sigue en la tabla con `superseded_at` informado y solo el nuevo está vigente

**AC2 — Enlace usado**
- **Given** un enlace vigente
- **When** se valida el correo con él
- **Then** queda con `used_at` informado y los demás del usuario, sustituidos

**AC3 — Un vigente por usuario**
- **Given** un usuario con un enlace vigente
- **When** se intenta insertar otro vigente sin sustituir el primero
- **Then** falla `uq_email_verification_one_active_per_user`

## 5. Plan de tareas

1. Migración `0009` y `EmailVerificationModel`.
2. `EmailVerification` y repositorio (`replace`, `get`, `mark_used`, purga), con su *fake* en `tests/fakes.py`.
3. Modelo de datos de `readme.md` (diagrama ER y §3.2).
4. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make migrate
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q -m db
$COMPOSE run --rm api alembic check
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] La migración se aplica y se revierte.
- [ ] `readme.md` refleja las columnas nuevas.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Retención de 30 días:** pasado ese plazo, un enlace antiguo vuelve a mostrarse como «no válido». Es aceptable porque el enlace caducó hace un mes.
- **Datos guardados:** se conservan más filas por usuario, pero solo con el hash del token y fechas; no hay datos personales nuevos.
