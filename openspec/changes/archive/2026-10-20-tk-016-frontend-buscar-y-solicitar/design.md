## Context

TK-015 expone `GET /v1/communities`, `POST /v1/communities/{id}/memberships` (409 con `status`) y `GET /v1/users/me/memberships`. TK-014 dejó `userApiFetch`, la cabecera y la página marcador de la comunidad.

## Goals / Non-Goals

**Goals:** búsqueda sin JavaScript; estado coherente tras solicitar (también con 409); aviso de acceso pendiente.

**Non-Goals:** listado de anuncios (TK-029).

## Decisions

- **Lecturas en `features/communities/data.ts`** (`server-only`, memorizadas con `cache` por petición): comunidad, búsqueda y mis membresías; las páginas no repiten llamadas.
- **`parseCommunitySearch`** (función pura) valida `searchParams`: recorta, ignora valores demasiado largos y páginas no numéricas.
- **`requestAccess` con `useActionState`:** `201` y `409` solo revalidan `/comunidades`, `/inicio` y la comunidad; la página vuelve a pintar el estado desde las membresías (AC4 sin mensaje de error).
- **`MembershipAction`** decide qué se muestra para cada estado (tabla del ticket), compartido por la búsqueda y la página de la comunidad.

## Risks / Trade-offs

- [Dos llamadas por página de búsqueda (comunidades y membresías)] → aceptable; las membresías del usuario son pocas.
