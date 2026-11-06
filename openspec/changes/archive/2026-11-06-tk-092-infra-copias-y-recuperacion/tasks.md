## 1. Infraestructura

- [x] 1.1 `infra/prod/restore.sh` con modo de ensayo y de producción, probado en local con PostgreSQL 16.15
- [x] 1.2 Copia previa a las migraciones pendientes en `deploy.sh`
- [x] 1.3 `restore.sh` en el documento de SSM (`modules/compute/deploy.tf`)

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: RPO y RTO, procedimientos, registro de ensayos, estructura y decisión

## 3. Verificación

- [x] 3.1 `make shellcheck`, `make tf-lint` y `make tf-plan`
- [x] 3.2 `make tf-apply` y despliegue (instala `restore.sh` y el nuevo `deploy.sh`)
- [x] 3.3 AC1: ensayo de `restore.sh` con la última copia; recuentos iguales a producción y tiempo medido
- [x] 3.4 AC2: volumen desde el último *snapshot*, PostgreSQL en un contenedor aparte y recuentos; volumen borrado
- [x] 3.5 AC3: imagen de un anuncio borrada y recuperada desde su versión anterior
- [x] 3.6 AC4: resultado de los ensayos en `infra/aws/README.md`; sin bases ni volúmenes de ensayo
