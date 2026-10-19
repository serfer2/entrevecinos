# TK-008 · Backend: inicio de sesión, autenticación JWT y `GET /v1/users/me`

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad y seguridad |
| **Componente** | `apps/api/` (área `users`, `infrastructure/security/`, `presentation/dependencies.py`) |
| **Historia** | HU-02 Iniciar sesión (Épica 1) |
| **Prioridad** | Alta (bloquea TK-009, TK-010 y todos los endpoints protegidos) |
| **Depende de** | TK-006 |
| **Referencias** | `docs/api/paths/auth_token.yaml`, `docs/api/paths/users_me.yaml` (`get`); esquemas `LoginRequest`, `AuthResponse`, `User`; `components/responses/Unauthorized.yaml`; `readme.md` §2.5 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-02 pide iniciar sesión con correo y contraseña, mostrar un error genérico si las credenciales no son correctas y proteger el contenido privado. TK-006 ya emite tokens y calcula *hashes*. Falta validar credenciales, validar tokens en cada petición protegida y que el frontend pueda conocer al usuario de la sesión.

**Objetivo:** implementar `POST /v1/auth/token` y la dependencia `get_current_user`, que será la base de autenticación de todos los endpoints protegidos, y `GET /v1/users/me`.

## 2. Alcance

**Incluye**
- Caso de uso `AuthenticateUser` y endpoint `POST /v1/auth/token`.
- `JwtTokenService.decode()` y dependencia `get_current_user` (`Authorization: Bearer`).
- Endpoint `GET /v1/users/me`.
- Pruebas unitarias y de integración, incluidos los casos de token inválido.

**No incluye**
- `PATCH /users/me` (TK-010) y `DELETE /users/me` (sin historia en el MVP de esta épica).
- Autorización por roles (RBAC): llegará con las comunidades (Épica 2).
- Limitación de peticiones, bloqueo por intentos fallidos, *refresh tokens* y cierre de sesión (ver §8).

## 3. Requisitos técnicos

### 3.1 Diseño por capas

```
domain/users/errors.py              # + InvalidCredentials
application/users/
├── ports.py                        # + UserRepository.get_by_id(), get_credentials(email)
│                                   #   TokenIssuer → TokenService con decode()
├── authenticate_user.py            # AuthenticateUser + LoginCommand
└── get_current_user.py             # GetCurrentUser(user_id)
infrastructure/security/jwt_tokens.py   # + decode(): firma, exp y algoritmo HS256 fijo
presentation/
├── dependencies.py                 # + get_current_user (HTTPBearer(auto_error=False))
└── v1/
    ├── auth.py                     # + POST /auth/token
    └── users.py                    # GET /users/me
```

- `get_credentials(email)` devuelve el usuario y su `password_hash` (o `None`). Así el *hash* nunca forma parte de la entidad `User`.

### 3.2 `POST /v1/auth/token` (público)

- **Petición** (`LoginRequest`, JSON, `extra="forbid"`): `email` y `password`. El contrato usa JSON, no el formulario OAuth2 de FastAPI.
- El correo se normaliza igual que en el registro.
- **200**: `AuthResponse`, igual que el registro.
- **401**: siempre `{"detail": "Correo o contraseña incorrectos."}` cuando el correo no existe, la contraseña no coincide, `is_active = false` o `deleted_at` no es nulo. El mensaje genérico es un requisito de HU-02 AC2.
- **422**: formato `ValidationError` sin `input` (manejador de TK-006).

**Tiempo de respuesta constante (asumido):** si el correo no existe, se verifica la contraseña contra un *hash* ficticio precalculado. Así la respuesta tarda lo mismo y no revela si la cuenta existe.

**Rehash:** si `pwdlib` indica que el *hash* usa parámetros antiguos (`verify_and_update`), se guarda el nuevo *hash* tras un inicio de sesión correcto (asumido).

### 3.3 Dependencia `get_current_user`

1. Lee `Authorization: Bearer <token>` con `HTTPBearer(auto_error=False)`.
2. `decode()` valida la firma, `exp` y que el algoritmo sea exactamente `HS256` (`algorithms=["HS256"]`). Rechaza `alg: none` y otros algoritmos.
3. Carga el usuario por `sub` y comprueba `is_active` y `deleted_at`.
4. Ante cualquier fallo (sin cabecera, token mal formado, firma inválida, token caducado, usuario inexistente, desactivado o eliminado) responde **401** `{"detail": "Autenticación requerida."}` con la cabecera `WWW-Authenticate: Bearer`.

En la especificación OpenAPI generada, las rutas que usan la dependencia muestran el esquema de seguridad `bearerAuth`.

### 3.4 `GET /v1/users/me`

- Protegido con `get_current_user`.
- **200**: `User` (`id`, `email`, `full_name`, `phone`, `avatar_url`, `platform_role`, `is_active`, `created_at`). `avatar_url` es `null` hasta que exista `media_asset` (asumido).
- **401**: según §3.3.

### 3.5 Pruebas

- Unitarias de `AuthenticateUser` con *fakes*: credenciales correctas, contraseña incorrecta, correo inexistente (se llama al *hasher* igualmente), usuario desactivado y usuario eliminado.
- Integración de `/auth/token`: comprobar que los cuatro casos de error devuelven exactamente el mismo estado y el mismo cuerpo.
- Integración de `/users/me`: sin cabecera, esquema distinto de `Bearer`, token mal formado, firma con otro secreto, token caducado (emitido con TTL negativo), token `alg: none`, usuario eliminado tras emitir el token, y caso correcto.

## 4. Criterios de aceptación

**AC1 — Acceso correcto (HU-02 AC1)**

- **Given** una cuenta registrada con `vecino@example.com`
- **When** envío `POST /v1/auth/token` con ese correo (con cualquier combinación de mayúsculas) y la contraseña correcta
- **Then** recibo `200` con `AuthResponse`, y el `access_token` permite llamar a `GET /v1/users/me`, que devuelve mis datos

**AC2 — Error genérico (HU-02 AC2)**

- **Given** el endpoint de inicio de sesión
- **When** envío un correo no registrado, una contraseña incorrecta, o las credenciales de una cuenta desactivada o eliminada
- **Then** en todos los casos recibo `401` con `detail: "Correo o contraseña incorrectos."`, sin diferencias en el estado ni en el cuerpo

**AC3 — Contenido protegido (HU-02 AC3, parte de la API)**

- **Given** un endpoint protegido (`GET /v1/users/me`)
- **When** lo llamo sin token, con un token caducado, mal firmado o con `alg: none`
- **Then** recibo `401` con `detail: "Autenticación requerida."` y la cabecera `WWW-Authenticate: Bearer`

**AC4 — Sin datos sensibles**

- **Given** cualquier respuesta de `/auth/token` o `/users/me`
- **When** reviso el cuerpo y los logs de la API
- **Then** no aparecen la contraseña, el *hash* ni el token (salvo `access_token` en la respuesta correcta)

## 5. Plan de tareas

1. Ampliar puertos y repositorio (`get_by_id`, `get_credentials`, actualización del *hash*).
2. Implementar `AuthenticateUser`, con el *hash* ficticio y el *rehash*, y sus pruebas unitarias.
3. Implementar `JwtTokenService.decode()` y `get_current_user`.
4. Implementar los routers `POST /auth/token` y `GET /users/me`.
5. Escribir las pruebas de integración de §3.5.
6. Comprobar que `/openapi.json` coincide con `auth_token.yaml` y `users_me.yaml` (`get`); actualizar `apps/api/README.md` (cómo proteger un endpoint) y verificar según la sección 6.

## 6. Verificación

```bash
make dev
TOKEN=$(curl -s -X POST http://localhost:8000/v1/auth/token -H 'Content-Type: application/json' \
  -d '{"email":"VECINO@example.com","password":"UnaClaveSegura123!"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
curl -s http://localhost:8000/v1/users/me -H "Authorization: Bearer $TOKEN"                       # 200
curl -s -X POST http://localhost:8000/v1/auth/token -H 'Content-Type: application/json' \
  -d '{"email":"vecino@example.com","password":"incorrecta-123"}'                                   # 401 genérico
curl -s -X POST http://localhost:8000/v1/auth/token -H 'Content-Type: application/json' \
  -d '{"email":"nadie@example.com","password":"incorrecta-123"}'                                    # 401 idéntico
curl -si http://localhost:8000/v1/users/me | grep -iE '^HTTP|www-authenticate'                    # 401 + Bearer
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan, y están cubiertos todos los casos de token de §3.5.
- [ ] `get_current_user` está documentado como la única forma de proteger endpoints.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Fuerza bruta:** no hay limitación de peticiones ni bloqueo por intentos. Se propone un ticket posterior con un límite por IP y por cuenta.
- **Revocación:** un token sigue siendo válido hasta `exp`, aunque cambie la contraseña. Mitigación parcial: la dependencia rechaza usuarios desactivados o eliminados. Una revocación completa (`token_version`) queda para cuando exista el cambio de contraseña.
- **Desfase de relojes:** `exp` se valida sin margen. Con un único servidor no es relevante.
