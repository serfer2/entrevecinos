## Context

TK-012 creó las tablas. Contrato: `communities.yaml` (`post`), `communities_community_id.yaml` (`get`), `CommunityCreate.yaml`, `Community.yaml`.

## Goals / Non-Goals

**Goals:** crear la comunidad y la membresía del creador en una transacción; 404 común reutilizable.

**Non-Goals:** búsqueda, solicitudes de acceso, roles (TK-015, TK-017), `PATCH`.

## Decisions

- **`CommunityRepository.add(community, admin_id)`** inserta comunidad y membresía `community_admin`/`approved` (`joined_at = reviewed_at = now()`, `reviewed_by` = creador) en la misma sesión; la sesión por petición confirma o revierte ambas.
- **`NotFoundError` en `domain/errors.py`:** los errores «no encontrado» de cada área heredan de ella y un único manejador responde 404.
- **Normalización en el esquema:** recorte de espacios y `""` → `null` en los opcionales; `name` en blanco → 422 en `body.name`.
- **`get` solo devuelve comunidades activas.**

## Risks / Trade-offs

- [Cualquier vecino puede crear comunidades] → moderación de comunidades fuera del MVP.
