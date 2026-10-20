# TK-004 · Automatización: Makefile para entornos de desarrollo

| Campo | Valor |
|---|---|
| **Tipo** | Tarea técnica / herramienta de desarrollo |
| **Componente** | `Makefile` (raíz del repo) |
| **Prioridad** | Media (mejora DX; no bloquea funcionalidad de producto) |
| **Depende de** | TK-001, TK-002, TK-003 |
| **Referencias** | `infra/docker-compose.yml` (TK-001 servicio `db`, TK-002 servicio `api`, TK-003 servicio `web`), `readme.md` §2.4 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo
TK-001, TK-002 y TK-003 definen los servicios `db`, `api` y `web` en `infra/docker-compose.yml`, pero cada operación (construir imágenes, levantar el entorno, limpiarlo) requiere invocar `docker compose --env-file .env -f infra/docker-compose.yml ...` manualmente con flags distintos. Esto es propenso a errores y ralentiza el onboarding de nuevos desarrolladores.

**Objetivo:** proveer un `Makefile` en la raíz del repositorio que exponga comandos cortos y memorables (`make build`, `make dev`, `make clean`, etc.) que envuelvan las operaciones de Docker Compose ya definidas, sin introducir lógica nueva de infraestructura.

## 2. Alcance
**Incluye**
- Fichero `Makefile` en la raíz del repo.
- Target `build-frontend`: construye únicamente la imagen del servicio `web`.
- Target `build-backend`: construye únicamente la imagen del servicio `api`.
- Target `build`: ejecuta `build-frontend` y `build-backend` (como prerequisitos de Make, sin duplicar comandos).
- Target `dev`: garantiza las imágenes construidas (depende de `build`) y levanta `db`, `api` y `web` en modo desarrollo.
- Target `clean`: detiene y elimina los contenedores de desarrollo y las imágenes Docker construidas localmente, **sin** eliminar el volumen de datos `db_data`.
- Target `help` (por defecto) que lista los comandos disponibles con una breve descripción.
- Validación mínima de que existe `.env` antes de ejecutar comandos que dependan de él.

**No incluye**
- Targets de producción/despliegue (`build-prod`, `deploy`) — no solicitados.
- Targets de test/lint/CI — corresponden a una entrega posterior.
- Modificación de `infra/docker-compose.yml` o de los `Dockerfile` de `api`/`web` — ya definidos en TK-001/02/03.
- Eliminación de volúmenes de datos (reset completo) — fuera de alcance; evita pérdida accidental de datos de desarrollo.

## 3. Requisitos técnicos

### 3.1 Variables y configuración común
```makefile
ENV_FILE     ?= .env
COMPOSE_FILE := infra/docker-compose.yml
COMPOSE      := docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE)
```
- `ENV_FILE` sobrescribible (`make dev ENV_FILE=.env.local`).
- Un único punto de verdad (`COMPOSE`) para no repetir flags en cada target.

### 3.2 Targets
| Target | Comando subyacente | Notas |
|---|---|---|
| `build-frontend` | `$(COMPOSE) build web` | Solo imagen `web` |
| `build-backend` | `$(COMPOSE) build api` | Solo imagen `api` |
| `build` | prerequisitos: `build-frontend build-backend` | No repite lógica |
| `dev` | prerequisito `build`; luego `$(COMPOSE) up -d db api web` | Detached `(asumido)`: no se especificó si debe seguir logs en foreground |
| `clean` | `$(COMPOSE) down --rmi local`; **no** usa `-v` | Preserva volumen `db_data` |
| `help` | `grep` de comentarios `##` sobre el propio Makefile | Target por defecto (`.DEFAULT_GOAL := help`) |

### 3.3 Buenas prácticas a aplicar
- `.PHONY: build-frontend build-backend build dev clean help` (ningún target genera un fichero con su mismo nombre).
- Comprobación temprana de `.env`: `test -f $(ENV_FILE) || (echo "Falta $(ENV_FILE); copia .env.example" && exit 1)` antes de targets que usan `$(COMPOSE)`.
- `SHELL := /bin/bash` y `.SHELLFLAGS := -eu -o pipefail -c` para que fallos en comandos encadenados no se silencien.
- Comentarios `##` junto a cada target para autodocumentación vía `help` (patrón estándar de Makefiles autodocumentados).
- Idempotencia: ejecutar `build`/`dev` repetidamente no debe fallar ni duplicar recursos.
- Nombres de target en kebab-case, igual que los solicitados.

## 4. Criterios de aceptación

**AC1 — build-frontend construye solo la imagen web**
- **Given** el repo con `infra/docker-compose.yml` definido y `.env` presente
- **When** se ejecuta `make build-frontend`
- **Then** se construye la imagen Docker del servicio `web` y no se reconstruyen `db` ni `api`

**AC2 — build-backend construye solo la imagen api**
- **Given** el repo con `infra/docker-compose.yml` definido y `.env` presente
- **When** se ejecuta `make build-backend`
- **Then** se construye la imagen Docker del servicio `api` y no se reconstruye `web`

**AC3 — build ejecuta ambas construcciones**
- **Given** ninguna imagen de `web` ni `api` construida previamente
- **When** se ejecuta `make build`
- **Then** ambas imágenes (`web` y `api`) quedan construidas, equivalente a ejecutar `build-frontend` y `build-backend`

**AC4 — dev levanta el entorno completo de desarrollo**
- **Given** `.env` configurado con los puertos por defecto (`API_PORT`, `WEB_PORT`)
- **When** se ejecuta `make dev`
- **Then** los servicios `db`, `api` y `web` quedan construidos (si no lo estaban) y en ejecución, y son accesibles en `http://localhost:${WEB_PORT:-3000}` y `http://localhost:${API_PORT:-8000}`

**AC5 — clean detiene el entorno sin perder datos**
- **Given** el entorno de desarrollo levantado por `make dev`
- **When** se ejecuta `make clean`
- **Then** los contenedores `db`, `api` y `web` se detienen y eliminan, las imágenes construidas localmente se eliminan, y el volumen `db_data` permanece intacto

## 5. Plan de tareas
1. Crear `Makefile` en la raíz con cabecera (`SHELL`, `.SHELLFLAGS`, `.DEFAULT_GOAL`, variables `ENV_FILE`/`COMPOSE_FILE`/`COMPOSE`).
2. Implementar target `help` autodocumentado a partir de comentarios `##`.
3. Implementar `build-frontend` y `build-backend`.
4. Implementar `build` como agregador vía prerequisitos de Make.
5. Implementar `dev` (prerequisito `build` + `up -d`), con mensaje final indicando las URLs de `web` y `api`.
6. Implementar `clean` (`down --rmi local`), verificando que `db_data` no se elimina.
7. Añadir comprobación de existencia de `.env` reutilizable por los targets que dependen de Compose.
8. Declarar todos los `.PHONY`.
9. Documentar los comandos disponibles en `infra/README.md` (o README raíz), enlazando a este ticket.
10. Probar manualmente el flujo completo (ver sección 6).

## 6. Verificación
```bash
# Pre-requisito: .env existente (ver TK-001)
test -f .env || cp .env.example .env

make help                 # lista los targets disponibles con descripción

make build-frontend        # construye solo la imagen 'web'
docker images | grep entrevecinos-web

make build-backend         # construye solo la imagen 'api'
docker images | grep entrevecinos-api

make build                 # equivalente a los dos comandos anteriores combinados

make dev                   # levanta db, api y web
docker compose --env-file .env -f infra/docker-compose.yml ps   # los 3 servicios activos/healthy
curl -f http://localhost:${WEB_PORT:-3000}/                      # responde la web
curl -f http://localhost:${API_PORT:-8000}/v1/health              # responde la api (una vez exista el endpoint; ver Riesgos)

make clean                 # detiene y elimina contenedores + imágenes locales
docker compose --env-file .env -f infra/docker-compose.yml ps   # sin servicios activos
docker images | grep entrevecinos          # sin imágenes locales residuales
docker volume ls | grep db_data            # el volumen persiste (no se elimina)
```

## 7. Definición de terminado
- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `make help` lista los 5 targets (`build-frontend`, `build-backend`, `build`, `dev`, `clean`) con descripción.
- [ ] Los targets son idempotentes (ejecutables varias veces sin error).
- [ ] `clean` no elimina el volumen `db_data`.
- [ ] Comandos documentados en `infra/README.md` o README raíz.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas
- **Modo de `dev` (detached vs foreground):** se asume `up -d` (background) ya que el usuario no especificó si debe seguir logs en vivo; si se prefiere, se puede añadir un target adicional `logs` en un ticket posterior (asumido).
- **`clean` y volúmenes:** se decide explícitamente NO usar `down -v`, para no borrar `db_data` por accidente; si se necesita un reset completo de datos, correspondería un target separado (p. ej. `clean-all`), fuera de alcance de este ticket.
- **Endpoint `/health` de `api`:** TK-002 aún no define un endpoint `/health` real (solo TCP check); la verificación con `curl /v1/health` en este ticket asume que dicho endpoint ya existirá para cuando se implemente TK-004, o se sustituye temporalmente por una comprobación de puerto (asumido).
- **Prefijo de nombres de imagen:** se asume que Docker Compose genera imágenes con prefijo `entrevecinos-` a partir de `name: entrevecinos` (TK-001), usado en los comandos de verificación (asumido).
