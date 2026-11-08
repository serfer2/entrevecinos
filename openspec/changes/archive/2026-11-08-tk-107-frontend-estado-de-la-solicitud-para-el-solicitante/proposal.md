## Why

HU-43 AC5 (Épica 8): con TK-106 la administración recibe un correo con cada solicitud y con TK-108 el vecino recibe otro cuando se aprueba, pero la web sigue diciendo solo «Tu solicitud está pendiente de aprobación…». El solicitante debe saber que su solicitud ha llegado a la administración y que le avisaremos por correo. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-43-recibir-un-aviso-por-correo-de-las-solicitudes-de-acceso/TK-107-frontend-estado-de-la-solicitud-para-el-solicitante.md`.

## What Changes

- **Aviso de solicitud pendiente** en `/comunidades/<id>`: «Hemos enviado tu solicitud a la administración de la comunidad, que la revisará. Te avisaremos por correo cuando la apruebe.».
- «Solicitud pendiente» se mantiene como etiqueta breve en `MembershipAction`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `web-communities`: texto del aviso de solicitud pendiente.

## Impact

- Web: `features/communities/components/AccessNotice.tsx` y su prueba nueva. Sin cambios en la API.
