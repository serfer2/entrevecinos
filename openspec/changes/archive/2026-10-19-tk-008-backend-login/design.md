## Context

TK-006 emite tokens y calcula hashes. Contratos: `auth_token.yaml` y `users_me.yaml` (`get`).

## Goals / Non-Goals

**Goals:** credenciales con un único error indistinguible; validación estricta del JWT; `get_current_user` como única forma de proteger endpoints.

**Non-Goals:** RBAC, limitación de peticiones, *refresh tokens*, cierre de sesión, `PATCH`/`DELETE /users/me`.

## Decisions

- **`PasswordHasher.verify_and_update(password, hash | None)`:** con `None` verifica contra un hash ficticio precalculado y devuelve `False`. El caso de uso nunca se salta la verificación, así el tiempo no revela si la cuenta existe.
- **`User.can_authenticate`:** `is_active` y sin `deleted_at`; lo usan el inicio de sesión y `get_current_user`.
- **Errores de dominio `InvalidCredentials` y `NotAuthenticated`:** se traducen a `401` en `presentation/errors.py`; `NotAuthenticated` añade `WWW-Authenticate: Bearer`.
- **`decode()` estricto:** `algorithms=["HS256"]` y `require=["exp", "iat", "sub"]`; cualquier `PyJWTError` o `sub` que no sea UUID → `NotAuthenticated`.
- **`HTTPBearer(auto_error=False, scheme_name="bearerAuth")`:** el error lo genera nuestra dependencia (mismo cuerpo en todos los casos) y el esquema de OpenAPI se llama como en el contrato.
- **Rehash dentro de la misma transacción** de la petición.

## Risks / Trade-offs

- [Fuerza bruta] → sin limitación de peticiones; ticket posterior.
- [Tokens válidos hasta `exp`] → mitigación parcial: se rechazan usuarios desactivados o eliminados.
