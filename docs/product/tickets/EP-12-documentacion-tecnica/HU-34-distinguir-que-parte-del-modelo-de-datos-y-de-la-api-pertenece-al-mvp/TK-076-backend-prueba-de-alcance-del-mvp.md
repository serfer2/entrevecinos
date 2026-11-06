# TK-076 · Backend: prueba que compara las rutas implementadas con el MVP del contrato

| Campo | Valor |
|---|---|
| **Tipo** | Backend / pruebas |
| **Componente** | `apps/api/tests/` (prueba nueva; `contract_dir()` de `test_listing_contact.py`) |
| **Historia** | HU-34 Distinguir qué parte del modelo de datos y de la API pertenece al MVP (Épica 12) |
| **Prioridad** | Media |
| **Depende de** | TK-074 |
| **Referencias** | `docs/api/openapi.yaml`; montaje `../docs/api:/docs/api:ro` del servicio `api` en `infra/docker-compose.yml`; TK-038 (primera prueba de contrato) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-074 alinea `x-mvp` con la implementación, pero nada impide que vuelvan a separarse al añadir un endpoint o cambiar el contrato. La API ya tiene una prueba de contrato (`test_owner_schema_matches_the_contract`) y el contrato montado en el contenedor.

**Objetivo:** que las pruebas fallen si las operaciones implementadas no coinciden con las marcadas `x-mvp: true`.

## 2. Alcance

**Incluye**
- Prueba que compara el conjunto `(método, ruta)` de `app.openapi()` (sin el prefijo `/v1`) con el de las operaciones `x-mvp: true` del contrato.
- Mensaje de error que lista las sobrantes en cada lado.
- Mover `contract_dir()` a `tests/api_helpers.py` para compartirlo (asumido).

**No incluye**
- Comparar esquemas o respuestas de cada operación.

## 3. Requisitos técnicos

- El contrato se lee siguiendo los `$ref` de `openapi.yaml` a `paths/*.yaml`; no requiere Node ni el bundle.
- Sin `docs/api` disponible, la prueba se omite (`pytest.skip`), como la de TK-038.
- Las rutas de FastAPI y las del contrato usan los mismos nombres de parámetros (`{community_id}`…); si no, la prueba debe normalizarlos.

## 4. Criterios de aceptación

**AC1 — Coinciden (HU-34 AC4)**
- **Given** la API y el contrato tras TK-074
- **When** se ejecutan las pruebas
- **Then** la prueba pasa

**AC2 — Endpoint nuevo sin contrato**
- **Given** un endpoint nuevo en la API sin `x-mvp: true` en el contrato
- **When** se ejecutan las pruebas
- **Then** la prueba falla y nombra el endpoint

**AC3 — MVP sin implementar**
- **Given** una operación del contrato marcada `x-mvp: true` sin implementar
- **When** se ejecutan las pruebas
- **Then** la prueba falla y nombra la operación

## 5. Plan de tareas

1. `contract_dir()` compartido.
2. Prueba de alcance.
3. Comprobar AC2 y AC3 cambiando temporalmente una marca.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check .
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Endpoints internos o de documentación de FastAPI** (`/docs`, `/openapi.json`): no aparecen en `app.openapi()["paths"]`, así que no interfieren.
