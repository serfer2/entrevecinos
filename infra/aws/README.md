# Producción en AWS

Guía de operación de producción de EntreVecinos y registro de sus decisiones de arquitectura. La infraestructura se define con Terraform en este directorio y se despliega en el proyecto de AWS en `eu-north-1`. Todo cambio en `infra/aws/`, `infra/prod/`, `infra/docker-compose.prod.yml` o `.github/workflows/` debe actualizar esta guía en el mismo cambio (ver `AGENTS.md`, §Convenciones).

> **Estado:** en construcción. La Épica 13 (`docs/product/tickets/EP-13-puesta-en-produccion-en-aws/`) completa cada sección con el ticket indicado. Hasta entonces, la infraestructura no existe.

## Estructura

*Pendiente: TK-078.* Organización de `infra/aws/` (`bootstrap/`, `modules/`, `envs/prod/`), versiones de Terraform y del proveedor, y comandos `make tf-*`.

## Puesta en marcha

*Pendiente: TK-078 a TK-087.* Requisitos (`aws login --profile entrevecinos`, Docker), límite de gasto, *bootstrap* del estado, orden de aplicación, variables de `prod.tfvars`, salidas y pasos manuales.

## Despliegue

*Pendiente: TK-086 y TK-090.* Compose de producción, `deploy.sh`, primer despliegue manual por SSM, despliegue continuo desde GitHub Actions y vuelta atrás.

## DNS

*Pendiente: TK-084 y TK-087.* Zona de Route 53 de `entrevecinos.org`, registros que crea Terraform y delegación desde Dinahosting.

## Secretos

*Pendiente: TK-082, TK-083 y TK-086.* Parámetros de `/entrevecinos/prod/` en Parameter Store, cómo llegan a los contenedores y cómo se rotan.

## Operación

*Pendiente: TK-091 a TK-093.* Registros, alarmas, copias y restauración, y *runbook* (`platform_admin`, rotaciones, actualizaciones, sustitución de la instancia).

## Costes

*Pendiente: TK-078 y TK-093.* Límite de gasto de 40 €/mes, presupuesto y estimación mensual por servicio.

## Decisiones de arquitectura

*Pendiente: TK-082 y TK-095.* Diferencias con la arquitectura prevista en el `readme.md` §2.4, motivo (ahorro de costes mientras el proyecto no escale), coste evitado y riesgo aceptado.

## Evolución

*Pendiente: TK-095.* Pasos recomendados cuando el proyecto sea maduro y tenga mucho tráfico, con su señal de disparo y su coste.

## Destruir el entorno

*Pendiente: TK-093.* Orden para eliminar la infraestructura sin gastar créditos y qué se conserva.
