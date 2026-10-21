# Convención de organización de tickets

```
docs/product/tickets/
├── 00-infra/                                  # tickets técnicos y transversales
└── EP-xx-<nombre-de-la-epica>/                # una carpeta por épica de user-stories.md
    └── HU-xx-<nombre-de-la-historia>/         # una subcarpeta por historia de usuario
        └── TK-yyy-<capa>-<descripcion>.md     # un fichero por ticket
```

- **Épicas:** `EP-xx-<nombre-de-la-epica>/`, donde `xx` es el número de la épica en `docs/product/user-stories.md` (p. ej. `EP-01-registro-y-perfil-basico/`).
- **Historias:** dentro de su épica, `HU-xx-<nombre-de-la-historia>/`, donde `xx` es el número de la HU en `docs/product/user-stories.md` (p. ej. `EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/`). La numeración de las HU sigue el orden en que se definen; una historia añadida después entre dos existentes lleva sufijo de letra para no renumerar (p. ej. `HU-09b`).
- **Tickets:** `TK-yyy-<capa>-<descripcion>.md`, con numeración global de tres dígitos (`TK-001`, `TK-012`…) y correlativa en todo el proyecto (no se reinicia por épica ni por historia). `<capa>` indica el componente principal: `bd`, `backend`, `frontend`, `infra`…
- **Tickets técnicos y transversales** que no pertenecen a una sola HU (infraestructura, herramientas de desarrollo, etc.) viven en `00-infra/`.

## Índice

| Carpeta | Tickets |
|---|---|
| `00-infra/` | TK-001 PostgreSQL · TK-002 esqueleto FastAPI · TK-003 esqueleto Next.js · TK-004 Makefile · TK-046 `Content-Security-Policy` · TK-062 documentación de la validación del correo |
| `EP-01-registro-y-perfil-basico/HU-01-registrarme-con-mi-correo-electronico/` | TK-005 persistencia y tabla `users` · TK-006 backend de registro · TK-007 formulario de registro |
| `EP-01-registro-y-perfil-basico/HU-02-iniciar-sesion/` | TK-008 backend de inicio de sesión y usuario actual · TK-009 inicio de sesión y rutas protegidas |
| `EP-01-registro-y-perfil-basico/HU-03-gestionar-mi-perfil-y-datos-de-contacto/` | TK-010 backend de actualización del perfil · TK-011 página de perfil |
| `EP-02-comunidades/HU-04-crear-una-comunidad/` | TK-012 tablas de comunidades y membresías · TK-013 backend crear comunidad · TK-014 crear comunidad y navegación |
| `EP-02-comunidades/HU-05-seleccionar-una-comunidad-y-solicitar-el-acceso/` | TK-015 backend buscar comunidades y solicitar acceso · TK-016 búsqueda, solicitud y mis comunidades |
| `EP-02-comunidades/HU-06-aprobar-o-rechazar-solicitudes-de-acceso/` | TK-017 autorización por comunidad y revisión de solicitudes · TK-018 gestión de solicitudes |
| `EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/` | TK-019 almacenamiento MinIO · TK-020 tablas de anuncios e imágenes · TK-021 subida y lectura de imágenes · TK-022 categorías y publicar anuncio · TK-023 formulario de publicación |
| `EP-03-gestion-de-anuncios/HU-08-editar-mis-anuncios/` | TK-024 backend editar anuncio e imágenes · TK-025 editar anuncio |
| `EP-03-gestion-de-anuncios/HU-09-eliminar-mis-anuncios/` | TK-026 backend eliminar anuncio · TK-027 eliminar con confirmación |
| `EP-03-gestion-de-anuncios/HU-09b-marcar-mi-anuncio-como-reservado-o-finalizado/` | TK-044 backend reservar y finalizar · TK-045 reservar y finalizar desde el detalle |
| `EP-04-explorar-y-encontrar-anuncios/HU-10-ver-los-anuncios-de-mi-comunidad/` | TK-028 backend listado · TK-029 listado de la comunidad |
| `EP-04-explorar-y-encontrar-anuncios/HU-11-buscar-anuncios-por-palabras-clave/` | TK-030 búsqueda de texto completo · TK-031 buscador |
| `EP-04-explorar-y-encontrar-anuncios/HU-12-filtrar-anuncios-por-comunidad-y-tipo/` | TK-032 backend filtros · TK-033 filtros y selector de comunidad |
| `EP-04-explorar-y-encontrar-anuncios/HU-13-ordenar-anuncios-por-fecha-o-precio/` | TK-034 backend ordenación · TK-035 selector de orden |
| `EP-05-detalle-y-contacto/HU-14-consultar-el-detalle-de-un-anuncio/` | TK-036 backend detalle · TK-037 página de detalle |
| `EP-05-detalle-y-contacto/HU-15-contactar-con-el-anunciante/` | TK-038 datos de contacto (contrato `ListingOwner.email`) · TK-039 contactar con el anunciante |
| `EP-06-administracion-minima/HU-16-gestionar-los-miembros-de-mi-comunidad/` | TK-040 backend bloquear y expulsar · TK-041 gestión de miembros |
| `EP-06-administracion-minima/HU-17-retirar-anuncios-problematicos/` | TK-042 backend retirar y restaurar anuncios · TK-043 retirar desde el detalle |
| `EP-07-mejora-de-funcionalidades-del-mvp/HU-18-acceder-a-la-aplicacion-desde-la-pagina-principal/` | TK-047 redirigir la raíz al inicio de sesión o al inicio |
| `EP-07-mejora-de-funcionalidades-del-mvp/HU-19-buscar-comunidades-al-registrarme-o-iniciar-sesion-si-no-pertenezco-a-ninguna/` | TK-048 lista de comunidades tras el registro o el inicio de sesión sin comunidades |
| `EP-07-mejora-de-funcionalidades-del-mvp/HU-20-entrar-en-mi-comunidad-al-iniciar-sesion-si-solo-pertenezco-a-una/` | TK-049 mi comunidad tras el inicio de sesión con una sola |
| `EP-08-mejora-de-la-gestion-de-comunidades/HU-21-aprobar-las-comunidades-nuevas-antes-de-activarlas/` | TK-050 backend comunidades pendientes y aprobación · TK-051 comunidades pendientes y página de aprobación |
| `EP-08-mejora-de-la-gestion-de-comunidades/HU-22-activar-al-momento-las-comunidades-que-crea-un-administrador-de-plataforma/` | TK-052 backend comunidades activas para el `platform_admin` |
| `EP-08-mejora-de-la-gestion-de-comunidades/HU-23-tener-una-sola-comunidad-pendiente-de-aprobacion-a-la-vez/` | TK-053 una comunidad pendiente por usuario (BD y backend) · TK-054 aviso de comunidad pendiente al crear |
| `EP-09-cierre-de-sesion/HU-24-cerrar-sesion/` | TK-055 cerrar sesión desde la cabecera |
| `EP-10-validacion-del-correo-electronico/HU-25-validar-mi-correo-electronico-al-registrarme/` | TK-056 envío de correo y Mailpit · TK-057 BD de la validación · TK-058 backend registro y validación · TK-060 aviso y validación desde el enlace |
| `EP-10-validacion-del-correo-electronico/HU-26-recibir-de-nuevo-el-correo-de-validacion/` | TK-059 backend correo pendiente y reenvío · TK-061 reenviar el correo de validación |
| `EP-10-validacion-del-correo-electronico/HU-27-entender-por-que-no-funciona-un-enlace-de-validacion-antiguo/` | TK-063 BD enlaces usados y sustituidos · TK-064 backend motivo del enlace no válido · TK-065 mensaje del enlace sustituido |

## Orden de implementación recomendado

Respeta las dependencias de cada ticket (campo **Depende de**). Los números de migración (`0002`…`0009`) asumen este orden.

**Estado:** los tickets TK-001 a TK-055 están implementados en este orden, con un cambio de OpenSpec archivado (`openspec/changes/archive/`) y un commit por ticket. También están implementados los de la Épica 10 (TK-056 a TK-062), con un commit por historia y otro para la documentación. TK-063 a TK-065 (HU-27) están pendientes.

| Bloque | Orden |
|---|---|
| Épica 1 | TK-005 → TK-011 |
| Épica 2 — Comunidades | TK-012 → TK-013 → TK-014 → TK-015 → TK-016 → TK-017 → TK-018 |
| Épica 3 — Publicar | TK-019 → TK-020 → TK-021 → TK-022 → TK-023 → TK-046 |
| Listado, detalle y borrado | TK-026 → TK-028 → TK-029 → TK-036 → TK-037 |
| Edición y eliminación (interfaz) | TK-024 → TK-025 → TK-027 |
| Búsqueda, filtros y orden | TK-030 → TK-031 → TK-032 → TK-033 → TK-034 → TK-035 |
| Contacto | TK-038 → TK-039 |
| Administración | TK-040 → TK-041 → TK-042 → TK-043 |
| Reservar y finalizar | TK-044 → TK-045 |
| Épica 7 — Mejoras | TK-047 → TK-048 → TK-049 |
| Épica 8 — Gestión de comunidades | TK-050 → TK-051 → TK-052 → TK-053 → TK-054 |
| Épica 9 — Cierre de sesión | TK-055 |
| Épica 10 — Validación del correo | TK-056 → TK-057 → TK-058 → TK-059 → TK-060 → TK-061 → TK-062 → TK-063 → TK-064 → TK-065 |

El detalle del anuncio (TK-036/TK-037) se adelanta a la edición y la eliminación de la interfaz porque es su punto de entrada. La CSP (TK-046) va justo después de TK-023, en cuanto se sirven imágenes desde el almacenamiento. Reservar y finalizar (TK-044/TK-045) va al final porque amplía el endpoint de estado de TK-042.
