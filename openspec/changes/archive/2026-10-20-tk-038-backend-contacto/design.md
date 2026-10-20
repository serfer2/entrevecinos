## Context

`ListingOwner` del dominio ya incluía `email` (TK-022) y `Listing` solo lo devuelven endpoints que exigen membresía aprobada (`require_member` en el listado y `ListingVisibility` en el detalle).

## Goals / Non-Goals

**Goals:** exponer el correo solo dentro de `Listing`; comprobarlo con pruebas de exposición y de contrato.

**Non-Goals:** preferencias de privacidad del anunciante; mensajería interna.

## Decisions

- **Campo nuevo y obligatorio** en `ListingOwner` (cambio compatible para los clientes).
- **`Membership.user` sigue siendo `UserSummary`**, sin contacto.
- **Prueba de contrato** que compara el esquema generado por FastAPI con `docs/api/components/schemas/ListingOwner.yaml`; `docs/api` se monta en solo lectura en `/docs/api` del contenedor `api` (si no está disponible, la prueba se omite).

## Risks / Trade-offs

- [El anunciante no puede ocultar su correo] → preferencias de privacidad en un ticket posterior.
