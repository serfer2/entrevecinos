# TK-010 · Backend: actualizar el perfil propio (`PATCH /v1/users/me`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `users`) |
| **Historia** | HU-03 Gestionar mi perfil y datos de contacto (Épica 1) |
| **Prioridad** | Media |
| **Depende de** | TK-008 |
| **Referencias** | `docs/api/paths/users_me.yaml` (`patch`); esquemas `UserUpdate`, `User`; `readme.md` §3.2 (`user`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-03 pide consultar y editar el nombre y el teléfono, con el nombre obligatorio. La consulta ya está cubierta por `GET /v1/users/me` (TK-008). Falta la edición.

**Objetivo:** implementar `PATCH /v1/users/me` para actualizar parcialmente `full_name` y `phone` del usuario autenticado.

## 2. Alcance

**Incluye**
- Caso de uso `UpdateProfile` y método `UserRepository.update_profile()`.
- Endpoint `PATCH /v1/users/me` con actualización parcial.
- Pruebas unitarias y de integración.

**No incluye (asumido)**
- `avatar_asset_id`: depende de `POST /media` y `media_asset`, que todavía no existen.
- Cambio de contraseña (`password` + `current_password`): no forma parte de HU-03.
- Cambio de correo: el contrato no lo permite.
- Hasta que se implementen, esos campos del contrato `UserUpdate` se rechazan con `422`. Es una diferencia temporal con `docs/api/components/schemas/UserUpdate.yaml`, que se documenta en la descripción del endpoint.

## 3. Requisitos técnicos

### 3.1 Diseño por capas

```
application/users/
├── ports.py              # + UserRepository.update_profile(user_id, changes) -> User
└── update_profile.py     # UpdateProfile + ProfileChanges
presentation/v1/
├── schemas/users.py      # + UserUpdateRequest
└── users.py              # + PATCH /users/me
```

- `ProfileChanges` distingue entre «campo no enviado» y «campo enviado con `null`». En la presentación se construye a partir de `model_fields_set` de Pydantic.
- El repositorio actualiza solo los campos enviados y `updated_at`, en una sola transacción. Si hay un error, no se modifica nada (HU-03 AC3).

### 3.2 Contrato

`PATCH /v1/users/me` (requiere `get_current_user`):

- **Petición** (`UserUpdateRequest`, `extra="forbid"`, al menos un campo):
  - `full_name`: se recortan los espacios; de 1 a 120 caracteres; no admite `null`.
  - `phone`: `string | null`; se recortan los espacios; `""` o `null` borran el teléfono; máximo 32 caracteres. Formato permisivo `^\+?[0-9 ()-]{6,32}$` (asumido), para aceptar números nacionales e internacionales sin imponer E.164.
- **200**: `User` actualizado.
- **401**: sin sesión válida (TK-008).
- **422**: cuerpo vacío, `full_name` vacío o solo con espacios, `full_name: null`, teléfono con formato inválido, o campos no implementados (`avatar_asset_id`, `password`, `current_password`) o desconocidos.
- El `404` del contrato no se produce en la práctica: si el usuario autenticado ya no existe, `get_current_user` responde `401`.

### 3.3 Datos mostrados en los anuncios (HU-03 AC2)

HU-03 AC2 pide que el nombre actualizado también aparezca en «mis anuncios». Para que se cumpla automáticamente cuando existan, los anuncios deben leer los datos del anunciante de la tabla `users` (`ListingOwner`), **sin copiarlos** en `listing` (asumido). Se deja anotado como requisito para los tickets de la Épica 3.

### 3.4 Pruebas

- Unitarias de `UpdateProfile`: solo nombre, solo teléfono, borrar teléfono con `null`, nombre recortado.
- Integración: los casos de §3.2, y que tras un `422` los datos guardados no cambian. Además, que `updated_at` aumenta y `created_at` no cambia.

## 4. Criterios de aceptación

**AC1 — Edición correcta (HU-03 AC2)**

- **Given** que he iniciado sesión
- **When** envío `PATCH /v1/users/me` con `{"full_name": "Alex Vecino García", "phone": "+34 600 111 222"}`
- **Then** recibo `200` con los datos actualizados, y un `GET /v1/users/me` posterior devuelve los mismos valores

**AC2 — Actualización parcial**

- **Given** que tengo un teléfono guardado
- **When** envío solo `{"full_name": "Nuevo nombre"}`
- **Then** el teléfono no cambia; y si después envío `{"phone": null}`, el teléfono se borra y el nombre se mantiene

**AC3 — Nombre obligatorio (HU-03 AC3)**

- **Given** que he iniciado sesión
- **When** envío `{"full_name": ""}`, `{"full_name": "   "}` o `{"full_name": null}`
- **Then** recibo `422` con `loc` `["body", "full_name"]` y mis datos guardados no cambian

**AC4 — Campos no permitidos**

- **Given** que he iniciado sesión
- **When** envío un cuerpo vacío, un teléfono con letras o campos como `email`, `platform_role` o `password`
- **Then** recibo `422` y no se modifica nada

**AC5 — Solo mi perfil**

- **Given** dos usuarios A y B
- **When** A envía `PATCH /v1/users/me`
- **Then** solo cambian los datos de A; y sin token se recibe `401`

## 5. Plan de tareas

1. Añadir `update_profile()` al puerto y al repositorio SQLAlchemy.
2. Implementar `UpdateProfile` y `ProfileChanges`, con sus pruebas unitarias.
3. Implementar `UserUpdateRequest` (validaciones de §3.2) y el endpoint `PATCH /users/me`.
4. Escribir las pruebas de integración (AC1–AC5).
5. Documentar en la descripción del endpoint la diferencia temporal con `UserUpdate.yaml`, y verificar según la sección 6.

## 6. Verificación

```bash
make dev
TOKEN=...   # obtenido con POST /v1/auth/token (ver TK-008)
curl -s -X PATCH http://localhost:8000/v1/users/me -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"full_name":"Alex Vecino García","phone":"+34 600 111 222"}'   # 200
curl -s -o /dev/null -w '%{http_code}\n' -X PATCH http://localhost:8000/v1/users/me \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"full_name":"   "}'          # 422
curl -s http://localhost:8000/v1/users/me -H "Authorization: Bearer $TOKEN"                                 # datos sin cambios
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan.
- [ ] La diferencia temporal con `UserUpdate.yaml` está documentada en el endpoint y en este ticket.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Formato del teléfono:** la validación es permisiva y no garantiza que el número exista. Si se necesitara normalizar a E.164, se usaría `phonenumbers`.
- **Visibilidad del teléfono:** HU-03 dice que sirve para que otros vecinos contacten. Quién puede verlo (solo los miembros de la comunidad) se decidirá en HU-14 y HU-15.
- **Campos pendientes del contrato:** avatar y contraseña necesitan tickets propios. Hasta entonces, el contrato publicado admite campos que la API rechaza.
