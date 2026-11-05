## 1. Compose y proxy

- [x] 1.1 `infra/docker-compose.prod.yml`: servicios, redes, endurecimiento, límites, *healthchecks*, `awslogs` y secretos `${VAR:?}`
- [x] 1.2 `infra/prod/proxy/default.conf.template` (nginx): `403` sin cabecera de origen, reenvío a `web:3000` sin ella y puerto de salud interno
- [x] 1.3 Prueba local del Compose (`config` sin secretos falla; arranque de `proxy` sin *root* con `no-new-privileges`)

## 2. Despliegue

- [x] 2.1 `infra/prod/deploy.sh`: ECR, secretos al entorno, roles, migraciones, arranque, salud, vuelta atrás, copias y limpieza; `shellcheck` sin avisos
- [x] 2.2 `backup.sh` y su unidad: contenedor `db` por etiquetas y rutas de `/opt/entrevecinos/prod/`

## 3. Terraform

- [x] 3.1 Parámetro `/entrevecinos/prod/origin-verify`, grupos de logs y documento de SSM `entrevecinos-deploy`
- [x] 3.2 `make tf-lint` sin errores y `make tf-apply`

## 4. Documentación

- [x] 4.1 `infra/aws/README.md`: «Puesta en marcha», «Despliegue», «Secretos», «Operación», «Costes» y «Decisiones de arquitectura»

## 5. Verificación

- [x] 5.1 Imágenes `arm64` en ECR y primer despliegue con `entrevecinos-deploy` (AC1)
- [x] 5.2 Puertos y redes (AC2), cabecera de origen (AC3) y contenedores endurecidos (AC5)
- [x] 5.3 Vuelta atrás con una API que no arranca (AC4)
- [x] 5.4 Ningún secreto en disco ni en la salida del despliegue (AC6); primera copia con `backup.sh`
- [x] 5.5 `make tf-plan` sin cambios
