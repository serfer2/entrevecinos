# TK-006 · Backend: registro de usuario (`POST /v1/auth/register`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (las cuatro capas, área `users`) |
| **Historia** | HU-01 Registrarme con mi correo electrónico (Épica 1) |
| **Prioridad** | Alta (bloquea TK-007 y TK-008) |
| **Depende de** | TK-005 |
| **Referencias** | `docs/api/paths/auth_register.yaml`; esquemas `RegisterRequest`, `AuthResponse`, `User`, `Error`, `ValidationError`; `readme.md` §2.5 (JWT, gestión de secretos), §3.2 (`user`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-01 pide que un visitante cree una cuenta con nombre, correo y contraseña, y que entre en la aplicación con la sesión iniciada. El contrato `POST /auth/register` responde `201` con `AuthResponse` (token JWT + usuario), `409` si el correo ya existe y `422` si los datos no son válidos.

**Objetivo:** implementar el endpoint de registro siguiendo la arquitectura limpia. Incluye la emisión de JWT y el *hash* de contraseñas, que reutilizará el inicio de sesión (TK-008).

## 2. Alcance

**Incluye**
- Entidad de dominio `User`, normalización del correo y errores de dominio.
- Puertos `UserRepository`, `PasswordHasher` y `TokenIssuer`, y caso de uso `RegisterUser`.
- Adaptadores: repositorio SQLAlchemy, *hasher* Argon2 y emisor JWT.
- Configuración `JWT_SECRET` y `JWT_TTL_SECONDS`.
- Router `POST /v1/auth/register`, esquemas Pydantic y manejo de errores `409` y `422`.
- Pruebas unitarias del caso de uso y de integración del endpoint.

**No incluye**
- Inicio de sesión, validación del token y `GET /users/me` (TK-008).
- Verificación del correo por email, *captcha* y limitación de peticiones (fuera del MVP; ver §8).
- Pantalla de registro (TK-007).

## 3. Requisitos técnicos

### 3.1 Dependencias

- `pwdlib[argon2]` (asumido): *hash* Argon2id. Se prefiere a `passlib`, que está sin mantenimiento.
- `pyjwt` (asumido): firma y validación de JWT.
- `pydantic[email]`: validación de correos (`EmailStr`).
- Añadir `pwdlib`, `jwt` y `email_validator` a las librerías prohibidas en `domain` y `application` (`test_architecture.py`).

### 3.2 Configuración

| Variable | Uso | Valor por defecto |
|---|---|---|
| `JWT_SECRET` | Clave de firma HS256 | — (obligatoria, mínimo 32 caracteres) |
| `JWT_TTL_SECONDS` | Duración del token de acceso | `86400` (24 h) (asumido) |

- `.env.example`: `JWT_SECRET=dev-only-change-me-0123456789abcdef` (valor ficticio de 32+ caracteres).
- `infra/docker-compose.yml` (servicio `api`): `JWT_SECRET: ${JWT_SECRET:?Define JWT_SECRET en .env}` y `JWT_TTL_SECONDS: ${JWT_TTL_SECONDS:-86400}`.
- El algoritmo se fija en código (`HS256`) y no es configurable, para que nunca se acepte `none` ni se confundan algoritmos.

### 3.3 Diseño por capas

```
domain/users/
├── entities.py        # User (dataclass): id, email, full_name, phone, platform_role, is_active, created_at…
├── value_objects.py   # normalize_email(): strip + lower
└── errors.py          # EmailAlreadyRegistered
application/users/
├── ports.py           # UserRepository, PasswordHasher, TokenIssuer (Protocol), AccessToken (dataclass)
└── register_user.py   # RegisterUser + RegisterUserCommand
infrastructure/
├── users/sqlalchemy_user_repository.py
└── security/
    ├── password_hasher.py   # Argon2PasswordHasher (pwdlib)
    └── jwt_tokens.py        # JwtTokenService: issue() (decode() en TK-008)
presentation/
├── dependencies.py    # get_session, get_user_repository, get_password_hasher, get_token_issuer
└── v1/
    ├── auth.py        # router /auth
    └── schemas/
        ├── auth.py    # RegisterRequest, AuthResponse
        └── users.py   # UserResponse
```

- `UserRepository`: `get_by_email(email) -> User | None` y `add(user, password_hash) -> User`. `add` traduce la violación de `uq_users_email` a `EmailAlreadyRegistered`, lo que cubre registros simultáneos con el mismo correo.
- `RegisterUser.execute(command)`: normaliza el correo, comprueba que no exista, calcula el *hash*, guarda el usuario y emite el token. Devuelve `(User, AccessToken)`.
- La entidad `User` nunca contiene el *hash* de la contraseña. El repositorio lo recibe aparte.

### 3.4 Contrato del endpoint

`POST /v1/auth/register` (público):

- **Petición** (`RegisterRequest`, `extra="forbid"`):
  - `email`: `EmailStr`, máximo 320 caracteres; se normaliza a minúsculas.
  - `password`: de 12 a 128 caracteres. No se aplican reglas de composición (criterio NIST) (asumido).
  - `full_name`: se recortan los espacios; de 1 a 120 caracteres.
  - `phone`: opcional, máximo 32 caracteres; `""` se guarda como `null` (asumido).
- **201**: `AuthResponse` con `access_token`, `token_type: "Bearer"`, `expires_in` y `user` (`User`, sin `password_hash`).
- **409**: `{"detail": "El correo ya está en uso."}`.
- **422**: formato `ValidationError` del contrato (`loc`, `msg`, `type`).

### 3.5 Token JWT

- *Claims*: `sub` (id del usuario), `iat`, `exp` (`iat + JWT_TTL_SECONDS`).
- `expires_in` de la respuesta es igual a `JWT_TTL_SECONDS`.

### 3.6 Seguridad

- **422 sin datos sensibles:** el manejador por defecto de FastAPI devuelve el campo `input` con el valor enviado, contraseña incluida. Se registra un manejador de `RequestValidationError` que devuelve solo `loc`, `msg` y `type`, como define `ValidationError.yaml`.
- No se registran en los logs ni la contraseña ni el token.
- Al guardar, el *hash* se calcula con los parámetros por defecto de `pwdlib` para Argon2id.

## 4. Criterios de aceptación

**AC1 — Registro correcto**

- **Given** que no existe ninguna cuenta con `vecino@example.com`
- **When** envío `POST /v1/auth/register` con nombre, ese correo y una contraseña de 12 o más caracteres
- **Then** recibo `201` con un `access_token` válido cuyo `sub` es el `id` del usuario, `token_type: "Bearer"` y `user` sin datos de contraseña; y en la base de datos el usuario tiene `platform_role = 'user'` y un *hash* Argon2id (`$argon2id$…`)

**AC2 — Correo ya registrado (también con otras mayúsculas)**

- **Given** que existe una cuenta con `vecino@example.com`
- **When** me registro con `vecino@example.com` o con `Vecino@Example.COM`
- **Then** recibo `409` con `detail: "El correo ya está en uso."` y no se crea ninguna cuenta

**AC3 — Datos inválidos**

- **Given** el endpoint de registro
- **When** envío un correo mal formado, un nombre vacío o solo con espacios, una contraseña de menos de 12 caracteres o un campo no definido en el contrato
- **Then** recibo `422`, con un error por cada campo incorrecto cuyo `loc` lo identifica (`["body", "email"]`…), y no se crea la cuenta

**AC4 — Sin datos sensibles en la respuesta**

- **Given** una petición de registro con una contraseña demasiado corta
- **When** recibo la respuesta `422`
- **Then** el cuerpo no contiene el valor de la contraseña ni el campo `input`

**AC5 — Arquitectura y configuración**

- **Given** el código del backend
- **When** ejecuto `pytest` y arranco la API sin `JWT_SECRET`
- **Then** la prueba de arquitectura pasa con las nuevas librerías prohibidas en `domain` y `application`, y el arranque falla con un error de configuración que nombra `JWT_SECRET`

## 5. Plan de tareas

1. Añadir dependencias, `JWT_SECRET` y `JWT_TTL_SECONDS` (`Settings`, `.env.example`, Compose).
2. Dominio: `User`, `normalize_email`, `EmailAlreadyRegistered`.
3. Aplicación: puertos y `RegisterUser`, con pruebas unitarias usando *fakes* de los puertos.
4. Infraestructura: repositorio SQLAlchemy, `Argon2PasswordHasher` y `JwtTokenService.issue()`.
5. Presentación: esquemas, dependencias, router `/auth`, manejador de `RequestValidationError` y traducción de `EmailAlreadyRegistered` a `409`.
6. Pruebas de integración del endpoint (AC1–AC4) contra la base de datos de pruebas.
7. Ampliar `test_architecture.py`, actualizar `apps/api/README.md` y verificar según la sección 6.

## 6. Verificación

```bash
make dev
curl -s -X POST http://localhost:8000/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"vecino@example.com","password":"UnaClaveSegura123!","full_name":"Alex Vecino"}'   # 201
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"Vecino@Example.com","password":"UnaClaveSegura123!","full_name":"Otro"}'         # 409
curl -s -X POST http://localhost:8000/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"no-es-correo","password":"corta","full_name":" "}'                             # 422 sin "input"
docker compose --env-file .env -f infra/docker-compose.yml exec db \
  psql -U entrevecinos -c 'select email, left(password_hash, 10) from users;'                 # $argon2id
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
docker compose --env-file .env -f infra/docker-compose.yml run --rm api ruff check .
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan, y el caso de uso tiene pruebas unitarias sin base de datos.
- [ ] `/openapi.json` muestra `POST /v1/auth/register` con los mismos campos, límites y códigos que `docs/api/paths/auth_register.yaml`.
- [ ] No hay secretos reales en el repositorio; `JWT_SECRET` es obligatoria.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Enumeración de cuentas:** el `409` revela que un correo ya está registrado. Lo exige HU-01 AC2. Se mitigará con limitación de peticiones en un ticket posterior (asumido).
- **Sin verificación del correo:** cualquiera puede registrar un correo ajeno. Queda fuera del MVP.
- **Duración del token de 24 h sin *refresh token*:** simplifica el MVP. El cierre de sesión y la revocación también están fuera de alcance (`user-stories.md`).
- **Algoritmo HS256 con secreto compartido:** suficiente con un único emisor y verificador (la API). Si otro servicio tuviera que validar tokens, se pasaría a RS256.
