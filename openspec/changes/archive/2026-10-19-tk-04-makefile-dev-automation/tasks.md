## 1. Makefile

- [x] 1.1 Cabecera: `SHELL`, `.SHELLFLAGS`, `.DEFAULT_GOAL`, `ENV_FILE`, `COMPOSE_FILE`, `COMPOSE`, `.PHONY`
- [x] 1.2 `help` autodocumentado y `check-env`
- [x] 1.3 `build-frontend`, `build-backend` y `build`
- [x] 1.4 `dev` con mensaje de URLs
- [x] 1.5 `clean` con `down --rmi local` sin `-v`

## 2. Documentación

- [x] 2.1 Sección de comandos `make` en `infra/README.md`

## 3. Verificación

- [x] 3.1 `make help` y fallo sin `.env`
- [x] 3.2 `build-frontend`, `build-backend` y `build` construyen las imágenes esperadas
- [x] 3.3 `make dev` levanta los tres servicios y responden web y api
- [x] 3.4 `make clean` elimina contenedores e imágenes y conserva `db_data`; repetir `dev`/`clean` es idempotente
