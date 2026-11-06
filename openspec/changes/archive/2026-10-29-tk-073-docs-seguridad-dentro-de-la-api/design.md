## Context

| Mecanismo | Implementación |
|---|---|
| CORS | `CORSMiddleware` en `apps/api/.../presentation/main.py` (`CORS_ORIGINS`) |
| JWT Auth | `CurrentUserDep` → `JwtTokenService` (HS256), `presentation/dependencies.py` |
| RBAC | `CommunityAccess` (`application/authorization/`) y `platform_role` |
| Cabeceras HTTP | `headers()` de `apps/web/next.config.ts`; HSTS solo en producción |
| CSP | `apps/web/src/proxy.ts` con un *nonce* por petición (TK-046) |

En la API, el orden real de una petición es middleware CORS → dependencia de usuario actual → política de permisos → caso de uso.

## Decisions

- **Subgrafo anidado «FastAPI · Python» dentro de «Backend · contenedor Docker»:** muestra que la seguridad forma parte del mismo proceso, no un salto de red. Id `FASTAPI` para no chocar con el nodo `API`.
- **Cadena `CORS --> JWT --> RBAC --> API`:** refleja el orden de aplicación; las flechas a PostgreSQL, MinIO y SMTP siguen saliendo de `API`.
- **Nodo `HEADERS` en lugar de `HELMET`:** las cabeceras son configuración de Next.js. Las peticiones a la API salen de `NEXT`, no del nodo de cabeceras.
- **`U <-.- SMTP` en lugar de `SMTP -.-> U`:** misma flecha, pero evita que Mermaid coloque al usuario al final al anidar el subgrafo (comprobado con `mermaid-cli`).
- **Tickets copiados en §6 del README sin cambios:** documentan lo que se pidió en su momento.
- El diagrama propuesto completo está en TK-073 §3.1.

## Risks / Trade-offs

- [Subgrafos anidados en Mermaid] → renderizar con `mermaid-cli` y revisar la vista previa de GitHub.
