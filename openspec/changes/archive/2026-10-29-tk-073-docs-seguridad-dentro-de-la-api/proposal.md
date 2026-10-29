## Why

HU-33: la arquitectura del `readme.md` describe la seguridad como se planteó antes de implementarla. El diagrama (§2.1) dibuja una «Capa de seguridad» (CORS → JWT Auth → RBAC) entre el frontend y el backend, pero los tres viven dentro de la API (`CORSMiddleware`, `CurrentUserDep` con `JwtTokenService` y `CommunityAccess`). Además, §2.1, §2.2 y §2.5 atribuyen las cabeceras de la web a Helmet, que no se usa: están en `next.config.ts` y la CSP con *nonce* en `proxy.ts`. Ticket: `docs/product/tickets/EP-12-documentacion-tecnica/HU-33-ver-donde-se-aplica-la-seguridad-en-el-diagrama-de-arquitectura/TK-073-docs-seguridad-dentro-de-la-api.md`.

## What Changes

- §2.1, diagrama: sin «Capa de seguridad»; CORS, JWT Auth y RBAC dentro de un subgrafo «FastAPI · Python», antes de la lógica de negocio. «Helmet» pasa a «Cabeceras HTTP de seguridad» (`next.config.ts` + CSP con *nonce*). «Solicitudes API con JWT» va de Next.js a CORS; desaparece «Solicitud autorizada».
- §2.1, justificación: seguridad de la API dentro de FastAPI y cabeceras en Next.js, sin Helmet.
- §2.2: sin componente «Capa de seguridad»; CORS, JWT y roles en «API y lógica de negocio»; cabeceras y CSP en «Frontend web».
- §2.5: cabeceras de seguridad configuradas en Next.js en lugar de Helmet.

## Capabilities

### New Capabilities

### Modified Capabilities

Ninguna: solo documentación; el comportamiento de seguridad no cambia.

## Impact

- Solo `readme.md`. Sin cambios de código, contrato ni migraciones.
