# TK-049 · Frontend: llevar a mi comunidad tras el inicio de sesión si solo pertenezco a una

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`postLoginPath`, `features/auth`) |
| **Historia** | HU-20 Entrar en mi comunidad al iniciar sesión si solo pertenezco a una (Épica 7) |
| **Prioridad** | Alta |
| **Depende de** | TK-048, TK-029 |
| **Referencias** | `user-stories.md` HU-20 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-048, `postLoginPath` lleva a `/comunidades` a quien no tiene comunidades y a `/inicio` al resto. Un miembro de una sola comunidad tiene que pulsar en ella desde `/inicio` para ver sus anuncios.

**Objetivo:** que, sin `next`, el miembro aprobado de una sola comunidad llegue directamente a `/comunidades/{communityId}`.

## 2. Alcance

**Incluye**
- Ampliar `postLoginPath` con el caso de una sola membresía aprobada.

**No incluye**
- Recordar la última comunidad visitada para quien pertenece a varias (sin historia; asumido).
- El registro: una cuenta recién creada no tiene comunidades y siempre va a `/comunidades` (TK-048 §3.3).

## 3. Requisitos técnicos

### 3.1 Destino tras el inicio de sesión

- Membresías `approved` (mismo criterio que TK-048 §3.1):
  - ninguna → `/comunidades` (TK-048);
  - exactamente una → `/comunidades/{community.id}`;
  - dos o más → `HOME_PATH` (asumido: `/inicio` ya lista mis comunidades).
- Las membresías `pending`, `rejected` o `blocked` no cuentan, ni las de comunidades desactivadas: un usuario con una aprobada y otra pendiente va a la aprobada.
- Un `next` seguro sigue teniendo prioridad, y un error de la API sigue llevando a `HOME_PATH` (TK-048 §3.1 y §3.2).

### 3.2 Pruebas

- `postLoginPath`: una aprobada, una aprobada activa y otra en una comunidad desactivada, dos aprobadas.
- `login`: sin `next` y con una comunidad → `/comunidades/{id}`.

## 4. Criterios de aceptación

**AC1 — Una comunidad (HU-20 AC1)**
- **Given** un usuario con una sola membresía aprobada
- **When** inicia sesión desde `/iniciar-sesion`
- **Then** queda en el listado de anuncios de esa comunidad

**AC2 — Una aprobada y otra pendiente (HU-20 AC1)**
- **Given** un usuario aprobado en una comunidad activa y con una solicitud pendiente en otra
- **When** inicia sesión
- **Then** queda en la comunidad aprobada

**AC3 — Varias comunidades (HU-20 AC2)**
- **Given** un usuario aprobado en dos comunidades
- **When** inicia sesión
- **Then** queda en `/inicio`, con ambas en «Mis comunidades»

**AC4 — Destino solicitado (HU-20 AC3)**
- **Given** un miembro de una sola comunidad que abre `/perfil` sin sesión
- **When** inicia sesión desde `/iniciar-sesion?next=%2Fperfil`
- **Then** queda en `/perfil`

## 5. Plan de tareas

1. Caso de una membresía aprobada en `postLoginPath`, con pruebas.
2. Ampliar las pruebas de `login`.
3. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Usuario que creó una comunidad (queda como administrador aprobado): iniciar sesión → /comunidades/<id>
# Aprobarlo en una segunda comunidad → iniciar sesión → /inicio con las dos
# Sin sesión, abrir /perfil → iniciar sesión → /perfil
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Varias comunidades:** quien pertenece a varias sigue pasando por `/inicio`; recordar la última visitada necesitaría su propia historia.
