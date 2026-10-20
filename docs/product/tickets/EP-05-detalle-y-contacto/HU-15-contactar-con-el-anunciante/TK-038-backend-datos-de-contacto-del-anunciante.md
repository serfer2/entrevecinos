# TK-038 · Backend: datos de contacto del anunciante

| Campo | Valor |
|---|---|
| **Tipo** | Backend / contrato de la API |
| **Componente** | `apps/api/` (`ListingOwner`), `docs/api/components/schemas/ListingOwner.yaml` |
| **Historia** | HU-15 Contactar con el anunciante (Épica 5) |
| **Prioridad** | Alta |
| **Depende de** | TK-036 |
| **Referencias** | `user-stories.md` HU-15 (AC1–AC3); `docs/api/components/schemas/ListingOwner.yaml`; `readme.md` §1.2 (MVP: canal de contacto directo) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El MVP sustituye la mensajería interna por un canal de contacto directo. HU-15 pide mostrar el teléfono y/o el correo del anunciante, el correo si no hay teléfono, y nunca a quien no sea miembro aprobado. El contrato actual de `ListingOwner` incluye `phone` pero **no** `email`.

**Objetivo:** añadir `email` a `ListingOwner` (contrato y API) y garantizar que los datos de contacto solo llegan a miembros aprobados de la comunidad del anuncio.

## 2. Alcance

**Incluye**
- Cambio de contrato: `ListingOwner.email` (`string`, `format: email`) en `docs/api` (fuentes y `dist/openapi.bundled.yaml` regenerado con Redocly, `docs/api/README.md`).
- `ListingOwnerResponse` con `email`.
- Pruebas de que ninguna respuesta con `ListingOwner` llega a no miembros.

**No incluye**
- Preferencias de privacidad del anunciante (ocultar el correo o el teléfono): ver §8.
- Mensajería interna (post-MVP).

## 3. Requisitos técnicos

### 3.1 Contrato

```yaml
# ListingOwner.yaml
description: >-
  Anunciante. `phone` y `email` son el canal de contacto del MVP y solo se muestran a miembros
  aprobados de la comunidad del anuncio.
required: [id, full_name, email]
properties:
  email:
    type: string
    format: email
```

- Es un cambio compatible (campo nuevo). Se documenta en el changelog de `docs/api/README.md`.

### 3.2 Exposición

- `ListingOwner` aparece en `Listing`, que solo devuelven endpoints con `require_member` (TK-022, TK-028, TK-036). No se añade a ningún esquema accesible por no miembros (`Community`, `Membership`…).
- `Membership.user` (gestión de solicitudes) sigue usando `UserSummary`, sin contacto (TK-017 §3.2).

### 3.3 Pruebas

- `GET /v1/listings/{id}` y el listado incluyen `owner.email` y `owner.phone` para un miembro aprobado.
- Un usuario pendiente, rechazado, bloqueado o ajeno recibe `403` en ambos y ninguna respuesta contiene el correo del anunciante (comprobación sobre el cuerpo de error).
- Prueba de contrato: el esquema generado por FastAPI para `ListingOwner` coincide con `docs/api` (campos y obligatoriedad).

## 4. Criterios de aceptación

**AC1 — Canal de contacto (HU-15 AC1)**
- **Given** que soy miembro aprobado
- **When** pido el detalle de un anuncio
- **Then** `owner` incluye `email` y `phone` (este último `null` si el anunciante no lo informó)

**AC2 — Sin teléfono (HU-15 AC2)**
- **Given** un anunciante sin teléfono
- **When** pido el detalle
- **Then** `owner.phone` es `null` y `owner.email` está informado

**AC3 — Datos protegidos (HU-15 AC3)**
- **Given** que no he iniciado sesión o no soy miembro aprobado
- **When** pido el detalle o el listado
- **Then** recibo `401` o `403` y ninguna respuesta contiene el teléfono ni el correo del anunciante

**AC4 — Contrato actualizado**
- **Given** `docs/api`
- **When** ejecuto la validación de Redocly
- **Then** `ListingOwner` incluye `email` y el *bundle* está regenerado sin errores

## 5. Plan de tareas

1. Actualizar `ListingOwner.yaml`, regenerar el *bundle* y el changelog.
2. Añadir `email` a la respuesta y a la consulta de propietario.
3. Pruebas de exposición y de contrato; verificación según la sección 6.

## 6. Verificación

```bash
npx @redocly/cli lint docs/api/openapi.yaml && npx @redocly/cli bundle docs/api/openapi.yaml -o docs/api/dist/openapi.bundled.yaml
curl -s http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $MIEMBRO" | python3 -c 'import sys,json;print(json.load(sys.stdin)["owner"])'
curl -s http://localhost:8000/v1/listings/<id> -H "Authorization: Bearer $PENDIENTE"   # 403 sin datos
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `docs/api` y la API coinciden en `ListingOwner`.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Privacidad:** cualquier miembro aprobado ve el correo de todos los anunciantes de su comunidad. El texto de ayuda del perfil (TK-011) ya avisa del teléfono; conviene ampliarlo al correo y valorar un ajuste para ocultarlo.
- **Uso indebido del correo (spam):** la mensajería interna post-MVP evitaría exponerlo.
