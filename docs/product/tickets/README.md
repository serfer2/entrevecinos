# Convención de organización de tickets

```
docs/product/tickets/
├── 00-infra/                                  # tickets técnicos y transversales
└── EP-xx-<nombre-de-la-epica>/                # una carpeta por épica de user-stories.md
    └── HU-xx-<nombre-de-la-historia>/         # una subcarpeta por historia de usuario
        └── TK-yyy-<capa>-<descripcion>.md     # un fichero por ticket
```

- **Épicas:** `EP-xx-<nombre-de-la-epica>/`, donde `xx` es el número de la épica en `docs/product/user-stories.md` (p. ej. `EP-01-registro-y-perfil-basico/`).
- **Historias:** dentro de su épica, `HU-xx-<nombre-de-la-historia>/`, donde `xx` es el número de la HU en `docs/product/user-stories.md` (p. ej. `EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/`). La numeración de las HU sigue el orden en que se definen.
- **Tickets:** `TK-yyy-<capa>-<descripcion>.md`, con numeración global de tres dígitos (`TK-001`, `TK-012`…) y correlativa en todo el proyecto (no se reinicia por épica ni por historia). `<capa>` indica el componente principal: `bd`, `backend`, `frontend`, `infra`…
- **Tickets técnicos y transversales** que no pertenecen a una sola HU (infraestructura, herramientas de desarrollo, etc.) viven en `00-infra/`.

## Índice

| Carpeta | Tickets |
|---|---|
| `00-infra/` | TK-001 PostgreSQL · TK-002 esqueleto FastAPI · TK-003 esqueleto Next.js · TK-004 Makefile |
| `EP-01-registro-y-perfil-basico/HU-01-registrarme-con-mi-correo-electronico/` | TK-005 persistencia y tabla `users` · TK-006 backend de registro · TK-007 formulario de registro |
| `EP-01-registro-y-perfil-basico/HU-02-iniciar-sesion/` | TK-008 backend de inicio de sesión y usuario actual · TK-009 inicio de sesión y rutas protegidas |
| `EP-01-registro-y-perfil-basico/HU-03-gestionar-mi-perfil-y-datos-de-contacto/` | TK-010 backend de actualización del perfil · TK-011 página de perfil |

Orden de implementación recomendado para la Épica 1: TK-005 → TK-006 → TK-007 → TK-008 → TK-009 → TK-010 → TK-011.
