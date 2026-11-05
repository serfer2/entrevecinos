## 1. Infraestructura

- [x] 1.1 Estructura `infra/aws/` (bootstrap, envs/prod, modules), `.gitignore` y objetivos `make tf-*`
- [x] 1.2 Módulo `private-bucket` y `bootstrap/` con el bucket del estado
- [x] 1.3 `envs/prod`: *backend*, proveedores con alias `us_east_1`, etiquetas, versiones y lockfile multiplataforma
- [x] 1.4 Módulo `budget` y variables (`prod.tfvars.example`)
- [x] 1.5 `.tflint.hcl` y `.checkov.yaml` con excepciones justificadas

## 2. Documentación

- [x] 2.1 `infra/aws/README.md`: «Estructura», «Puesta en marcha» (límite de gasto, *bootstrap*, variables) y «Costes»

## 3. Aplicación en AWS

- [x] 3.1 Límite de gasto de 40 €/mes en AWS Settings (propietario del proyecto) y equivalente en USD anotado en «Costes»
- [x] 3.2 `make tf-bootstrap` y comprobación del bucket del estado (versionado, cifrado)
- [x] 3.3 `make tf-init`, `make tf-apply` del presupuesto y comprobación en AWS Budgets

## 4. Verificación

- [x] 4.1 `make tf-lint` sin errores
- [x] 4.2 Segundo `make tf-plan` sin cambios
