# TK-064 · Backend: motivo del enlace de validación no válido (`POST /v1/auth/email-verification`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `users`), `docs/api/` |
| **Historia** | HU-27 Entender por qué no funciona un enlace de validación antiguo (Épica 10) |
| **Prioridad** | Media |
| **Depende de** | TK-058, TK-063 |
| **Referencias** | `docs/api/paths/auth_email_verification.yaml`; `components/schemas/VerificationError.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`POST /auth/email-verification` responde el mismo `400 verification_invalid` para un token desconocido, uno ya usado y uno sustituido por un reenvío (TK-058 §3.4). Con TK-063 la API conserva los enlaces usados y sustituidos.

**Objetivo:** que la respuesta indique el motivo real para que la web muestre el mensaje adecuado.

## 2. Alcance

**Incluye**
- Nuevos `code` en el `400` de `verifyEmail`.
- Caso de uso `VerifyEmail` y `ResendEmailVerification` adaptados al repositorio de TK-063.
- Contrato y tabla de cambios de `docs/api/README.md`; `apps/api/README.md`.

**No incluye**
- Los mensajes de la web (TK-065).

## 3. Requisitos técnicos

### 3.1 Orden de comprobación en `VerifyEmail`

| Situación del token | Respuesta |
|---|---|
| No existe (nunca se envió o se purgó, TK-063 §3.3), o su usuario no existe o está eliminado | `400` `{"detail": "El enlace de validación no es válido.", "code": "verification_invalid"}` |
| Existe y la cuenta ya tiene el correo validado (el enlace se usó, o se sustituyó y la cuenta se validó con otro) | `400` `{"detail": "Tu correo ya está validado.", "code": "email_already_verified"}` |
| Existe, sustituido (`superseded_at`) y la cuenta sigue pendiente | `400` `{"detail": "Este enlace ya no es válido porque te hemos enviado uno más reciente.", "code": "verification_superseded", "email": "..."}` |
| Vigente y caducado | `410` `verification_expired` con `email`, como ahora |
| Vigente y sin caducar | `200` con `AuthResponse`, como ahora; el enlace queda usado (`mark_used`) |

- `email_already_verified` se decide por el estado de la cuenta (`email_verified_at`), no por el del enlace: un enlace sustituido de una cuenta ya validada responde así (HU-27 AC2).
- `verification_superseded` incluye el `email` para ofrecer el reenvío, con el mismo razonamiento que el `410`: quien tiene el token recibió el correo (TK-058 §3.4). Un token desconocido no revela nada (HU-27 AC4).
- Errores de dominio nuevos: `EmailAlreadyVerified` y `VerificationSuperseded(email)`; sus manejadores en `presentation/errors.py`.

### 3.2 Reenvío

- `ResendEmailVerification` no cambia de comportamiento; `EmailVerificationIssuer.issue` usa `replace`, que ahora marca los anteriores como sustituidos (TK-063).

### 3.3 Contrato

- `VerificationError.code`: enum `verification_expired`, `verification_invalid`, `verification_superseded`, `email_already_verified`; `email` solo con `verification_expired` y `verification_superseded`.
- `auth_email_verification.yaml`: ejemplos del `400` para cada `code`.
- `docs/api/README.md`, fila TK-064: «`verifyEmail`: el `400` distingue `verification_invalid`, `email_already_verified` y `verification_superseded` (con `email`)». Compatible para clientes que solo miran el estado.
- `VerificationErrorResponse.code` en `presentation/v1/schemas/auth.py` con los mismos valores.

### 3.4 Pruebas

- Token desconocido → `400 verification_invalid`.
- Token usado → `400 email_already_verified`.
- Token sustituido con la cuenta pendiente → `400 verification_superseded` con `email`; la cuenta sigue inactiva.
- Token sustituido con la cuenta ya validada con el nuevo → `400 email_already_verified`.
- Token sustituido y además caducado, cuenta pendiente → `400 verification_superseded` (la sustitución tiene prioridad: el usuario debe usar el último correo).
- Vigente: `200`, `410` sin cambios.

## 4. Criterios de aceptación

**AC1 — Sustituido (HU-27 AC1)**
- **Given** una cuenta pendiente que ha pedido un reenvío
- **When** se valida el token del primer correo
- **Then** se recibe `400` con `code: verification_superseded` y el correo, y la cuenta sigue inactiva

**AC2 — Ya validada (HU-27 AC2)**
- **Given** una cuenta validada
- **When** se valida el mismo token u otro anterior de esa cuenta
- **Then** se recibe `400` con `code: email_already_verified`

**AC3 — Desconocido (HU-27 AC3 y AC4)**
- **Given** un token que no se ha emitido nunca
- **When** se valida
- **Then** se recibe `400` con `code: verification_invalid`, sin correo

## 5. Plan de tareas

1. Errores de dominio y orden de comprobación en `VerifyEmail` (con `mark_used`).
2. Manejadores, esquemas y contrato; `docs/api/README.md` y `apps/api/README.md`.
3. Pruebas unitarias y de API.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
(cd docs/api && npx @redocly/cli lint openapi.yaml)
# Registrar, esperar 60 s, reenviar y validar el token del primer correo → 400 verification_superseded
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **`email` en `verification_superseded`:** solo lo recibe quien tiene un token emitido de verdad, que llegó a ese buzón; no amplía lo que ya expone el `410`.
