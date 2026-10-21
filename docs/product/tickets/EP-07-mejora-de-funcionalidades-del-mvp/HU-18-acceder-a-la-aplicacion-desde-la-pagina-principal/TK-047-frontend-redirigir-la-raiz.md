# TK-047 · Frontend: redirigir la raíz al inicio de sesión o al inicio

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / corrección |
| **Componente** | `apps/web/` (`src/app/page.tsx`) |
| **Historia** | HU-18 Acceder a la aplicación desde la página principal (Épica 7) |
| **Prioridad** | Alta |
| **Depende de** | TK-003, TK-009 |
| **Referencias** | `user-stories.md` HU-18 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Tras `make dev`, `http://localhost:3000` mostraba solo el título «EntreVecinos». `src/app/page.tsx` era el marcador de TK-003, que ninguna HU sustituyó, y ninguna página enlazaba con `/registro` ni con `/iniciar-sesion`. Los servicios respondían, pero desde la raíz no había forma de usar la aplicación.

**Objetivo:** que `/` lleve a `/iniciar-sesion` sin sesión y a `/inicio` con ella.

## 2. Alcance

**Incluye**
- Sustituir el marcador de `src/app/page.tsx` por una redirección según la sesión.

**No incluye**
- Una página de bienvenida con contenido propio para visitantes (sin historia; asumido).
- Cambios en `src/proxy.ts`: `/` sigue en `PUBLIC_ROUTES`, así que el proxy no la redirige.

## 3. Requisitos técnicos

### 3.1 Redirección

- `getCurrentUser()` (DAL de TK-009) decide el destino: usuario → `redirect(HOME_PATH)`; sin usuario → `redirect(LOGIN_PATH)`.
- Si la API falla, se trata como sin sesión (`.catch(() => null)`), igual que en `/iniciar-sesion` y `/registro`. Así se evita un bucle: con una cookie inválida, `/inicio` acabaría en el inicio de sesión de todos modos.
- Las constantes salen de `@/features/auth/routes`; no se repiten las rutas como literales.

### 3.2 Pruebas

- Sin prueba unitaria: la página solo encadena `getCurrentUser()` y `redirect()`. Se verifica contra el servicio levantado (sección 6).

## 4. Criterios de aceptación

**AC1 — Sin sesión (HU-18 AC1)**
- **Given** que no tengo la cookie de sesión
- **When** abro `http://localhost:3000/`
- **Then** recibo un `307` hacia `/iniciar-sesion` y el formulario muestra el enlace a `/registro`

**AC2 — Con sesión (HU-18 AC2)**
- **Given** que tengo una sesión válida
- **When** abro `http://localhost:3000/`
- **Then** llego a `/inicio`

**AC3 — API caída**
- **Given** que tengo una cookie de sesión pero la API no responde
- **When** abro `/`
- **Then** llego a `/iniciar-sesion`, sin error ni bucle de redirecciones

## 5. Plan de tareas

1. Redirección en `src/app/page.tsx`.
2. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" localhost:3000/
# 307 -> http://localhost:3000/iniciar-sesion
# Navegador: iniciar sesión → abrir / → /inicio
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Página de bienvenida:** si más adelante se quiere presentar EntreVecinos a los visitantes, `/` dejaría de ser una redirección y necesitaría su propia historia.
