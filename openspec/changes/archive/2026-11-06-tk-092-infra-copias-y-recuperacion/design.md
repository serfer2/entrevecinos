## Context

TK-082 dejó `backup.sh` (cada 6 horas, 30 días en S3), *snapshots* diarios del volumen (7) y contraseñas en Parameter Store; TK-080, el versionado del bucket de imágenes (versiones anteriores, 30 días). Faltan la restauración, los procedimientos y la prueba de que funcionan.

## Goals / Non-Goals

**Goals:** restaurar sin improvisar, ensayado y con tiempos medidos; no perder la base actual al restaurar.

**Non-Goals:** recuperación a un punto en el tiempo (WAL), AWS Backup y copias en otra región o cuenta.

## Decisions

- **Restaurar siempre en una base nueva y cambiar nombres.** El ticket preveía `pg_restore --clean --if-exists` sobre la base de producción. `restore.sh` restaura en una base nueva y, en producción, renombra (`entrevecinos` → `entrevecinos_anterior_<fecha>`, la restaurada → `entrevecinos`): la base anterior sigue intacta para volver atrás al instante, el corte es de segundos (solo el cambio de nombre con la API parada) y se evitan los problemas de `--clean` con el esquema `public` y la extensión `unaccent`. Además de la copia previa con `backup.sh`.
- **Restaurar como `entrevecinos_owner`, crear la base como `postgres`.** Los objetos quedan del propietario, como tras las migraciones; `postgres` solo crea, borra y renombra bases y aplica los permisos de `entrevecinos_app` (los mismos de `10-roles.sh`). Las contraseñas se leen de Parameter Store en el proceso y llegan a `docker exec` por entorno.
- **Solo bases `entrevecinos_*`** como destino: un error de escritura no puede borrar `postgres` ni las plantillas, y producción solo se sustituye con `--production --yes`.
- **Copia previa en el despliegue solo si hay migraciones pendientes** (`alembic current` de la imagen nueva sin «(head)»); en la primera instalación (base vacía) no se copia porque `backup.sh` la daría por fallida.
- **Ensayo desde *snapshot* con un volumen de lectura y escritura.** El ticket pedía montarlo en solo lectura, pero PostgreSQL necesita escribir (recuperación tras un *snapshot* consistente ante caídas). El volumen es una copia desechable: se monta con `nouuid` (mismo UUID de XFS que el de producción), PostgreSQL arranca en un contenedor sin red y se borra todo al terminar.

## Risks / Trade-offs

- **Copias en la misma cuenta y región:** un administrador puede borrarlas y un fallo de la región se lleva todo. S3 Object Lock en modo *governance* queda como mejora (TK-095).
- **Retención de 30 días:** un error de datos detectado más tarde no se puede deshacer.
- **Base anterior conservada:** ocupa disco en el volumen de datos hasta que se borra a mano (la alarma `disk-data` avisa).
