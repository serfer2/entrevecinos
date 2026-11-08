# TK-107 · Frontend: el solicitante sabe que la administración revisará su solicitud

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/communities`: `AccessNotice`, `MembershipAction`) |
| **Historia** | HU-43 Recibir un aviso por correo de las solicitudes de acceso (Épica 8); también HU-44 |
| **Prioridad** | Baja |
| **Depende de** | TK-016, TK-106, TK-108 |
| **Referencias** | `features/communities/components/AccessNotice.tsx` (`NOTICES.pending`); `MembershipAction.tsx` («Solicitud pendiente») |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-106, la administración de la comunidad recibe un correo con cada solicitud. Hoy el solicitante ve «Tu solicitud está pendiente de aprobación. Podrás ver y publicar anuncios cuando un administrador la apruebe.», sin saber si alguien se ha enterado.

**Objetivo:** que el solicitante sepa que su solicitud ha llegado a la administración, que la revisará y que recibirá un correo cuando la apruebe (HU-43 AC5, TK-108).

## 2. Alcance

**Incluye**
- Texto del aviso de solicitud pendiente en la página de la comunidad.
- Texto tras pulsar «Solicitar acceso», si se muestra alguno.

**No incluye**
- El correo de aprobación (TK-108).

## 3. Requisitos técnicos

- `AccessNotice`, estado `pending`: «Hemos enviado tu solicitud a la administración de la comunidad, que la revisará. Te avisaremos por correo cuando la apruebe.» (asumido: «enviado a la administración» es cierto aunque no salga el aviso a la administración, porque la solicitud aparece en su lista de pendientes; si el correo de aprobación no sale por falta de cupo, la comunidad aparece igualmente en «Mis comunidades»).
- `MembershipAction`: mantener «Solicitud pendiente» como etiqueta breve.
- Revisar las pruebas que comprueban el texto anterior.

## 4. Criterios de aceptación

**AC1 — Solicitud enviada (HU-43 AC5)**
- **Given** un vecino con una solicitud pendiente en una comunidad
- **When** abre la página de la comunidad
- **Then** ve «Hemos enviado tu solicitud a la administración de la comunidad, que la revisará. Te avisaremos por correo cuando la apruebe.»

## 5. Plan de tareas

1. Texto de `AccessNotice` y pruebas.
2. Verificación según la sección 6.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [x] El criterio de aceptación se cumple.
- [x] Lint, tipos y pruebas de la web pasan.
- [ ] Cambios revisados y fusionados mediante *pull request*.
