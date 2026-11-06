## 1. Documentación

- [x] 1.1 `infra/aws/README.md`: esqueleto con las secciones (estructura, puesta en marcha, despliegue, DNS, secretos, operación, costes, decisiones de arquitectura, evolución, destrucción), cada una con el ticket que la completará
- [x] 1.2 `infra/README.md`: enlace a `infra/aws/README.md`
- [x] 1.3 `openspec/config.yaml`: párrafo de infraestructura de producción y rutas de infraestructura en `context`; reglas nuevas en `proposal`, `design` y `tasks`
- [x] 1.4 `AGENTS.md`: viñeta «Infraestructura» en §Convenciones
- [x] 1.5 `.github/pull_request_template.md`: plantilla con la casilla de `infra/aws/README.md`
- [x] 1.6 Tickets: TK-089 incorpora el trabajo `docs-infra`; TK-094 y `docs/product/tickets/README.md` reflejan el aplazamiento y el estado

## 2. Verificación

- [x] 2.1 `openspec instructions proposal|design|tasks` de este change muestran las reglas nuevas (la configuración carga sin errores)
- [x] 2.2 Las cuatro rutas coinciden en `openspec/config.yaml`, `AGENTS.md` y la plantilla (`grep`)
- [x] 2.3 `openspec validate tk-094-docs-regla-de-documentacion-de-la-infraestructura` sin errores
