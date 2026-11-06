## Context

Decisión del proyecto: sin alta disponibilidad mientras no escale, PostgreSQL en la instancia con cuatro mitigaciones (copias cada 6 h, alarma de copias, volumen separado, usuario sin privilegios). La instancia (TK-085) y el Compose (TK-086) aún no existen.

## Goals / Non-Goals

**Goals:** datos que sobreviven a la instancia, copias comprobadas e imborrables desde la instancia, mínimo privilegio en la base.

**Non-Goals:** contenedor `db` y despliegue (TK-086), adjunto del volumen (TK-085), alarma (TK-091), restauración (TK-092).

## Decisions

- **Roles con `\gexec`** y contraseñas como variables de `psql` desde el entorno: el mismo *script* sirve para la inicialización y para cada despliegue, y aplica las rotaciones.
- **`REVOKE CREATE ON SCHEMA public FROM PUBLIC`** y privilegios por defecto de `entrevecinos_owner`: las tablas nuevas de las migraciones quedan disponibles para la API sin DDL.
- **Denegación de borrado por `aws:PrincipalArn`** en el bucket de copias: la caducidad del ciclo de vida la ejecuta S3 y no le afecta.
- **`pg_dump` en *streaming*** (`aws s3 cp -`) sin copia en disco y verificación leyendo la copia subida.
- **Contraseñas sin caracteres especiales** (40 caracteres alfanuméricos): sin problemas de escape en URL de conexión.

## Risks / Trade-offs

- [RPO de 6 horas] → aceptado; la evolución es RDS con PITR.
- [Quien comprometa la instancia accede a la base] → usuario sin privilegios y copias imborrables; no se elimina el riesgo.
