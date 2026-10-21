## Context

TK-050 crea las comunidades inactivas y expone `GET/PATCH /v1/admin/communities`. El usuario de la sesión trae `platform_role`.

## Decisions

- **Destino según `is_active` de la respuesta:** así el caso del `platform_admin` (TK-052) no necesita más cambios.
- **`/admin/comunidades` responde `notFound()` a quien no es `platform_admin`:** no revela la página.
- **Resultado en la URL (`?resultado=aprobada|error`)**, como la revisión de solicitudes (TK-018).
- **Acceso desde `/inicio`** en lugar de un menú de administración en la cabecera, que no conoce al usuario.

## Risks / Trade-offs

- [Sin notificaciones] → el creador ve la aprobación al volver a `/inicio`.
