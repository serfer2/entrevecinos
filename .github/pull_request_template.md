## Qué cambia y por qué

<!-- Historia (HU-xx) y ticket (TK-yyy) de docs/product/tickets/; resumen del cambio. -->

## Comprobaciones

- [ ] Pruebas, lint y formato pasan en contenedores (ver `AGENTS.md`, «Entorno y comandos»).
- [ ] Si cambia una petición o respuesta de la API, he actualizado `docs/api/openapi.yaml`.
- [ ] Si cambia el modelo de datos, hay una migración Alembic revisada a mano, con `downgrade()`.
- [ ] Si cambia la infraestructura (`infra/aws/`, `infra/prod/`, `infra/docker-compose.prod.yml` o `.github/workflows/`), he actualizado `infra/aws/README.md`.
