## Context

Las épicas anteriores dejaron cada pieza documentada en su ticket dentro de `infra/aws/README.md`, pero `readme.md` seguía con la arquitectura prevista y faltaban el *runbook*, los costes y la destrucción.

## Goals / Non-Goals

**Goals:** que el `readme.md` describa lo desplegado y que la guía cubra la operación completa.

**Non-Goals:** resumen de todas las decisiones y evolución recomendada (TK-095).

## Decisions

- **Dos diagramas en §2.4**, desarrollo local y producción, en vez de uno: juntos no se leían. El de producción incluye GitHub (Actions y ECR) porque el despliegue forma parte de la arquitectura.
- **El readme resume y enlaza**: el detalle (comandos, umbrales, procedimientos) vive solo en `infra/aws/README.md`, para que no haya dos versiones que mantener.
- **Costes con dos cifras**: el gasto real sin créditos (Cost Explorer) y la estimación a precio de lista; mientras duren los créditos del plan FREE, la factura es 0.
- **Actualización mayor de PostgreSQL con copia y restauración** (nuevo `PGDATA` en el mismo volumen y `restore.sh`), sin `pg_upgrade`: reutiliza herramientas ya ensayadas y deja el clúster anterior para volver atrás.
- **Destrucción no ensayada**: destruiría producción; el orden se basa en los bloqueos conocidos (`prevent_destroy`, protección contra la terminación, clave del usuario de CI, buckets y repositorios con contenido, *snapshots* fuera de Terraform).

## Risks / Trade-offs

- **Procedimientos sin ensayar** (destrucción, reemplazo de la instancia, actualización mayor, migración a RDS): pueden tener pasos que fallen; se revisan la primera vez que se usen.
- **Precios de lista** cambian; la estimación se revisa con el gasto real.
