# Comandos de desarrollo de EntreVecinos (TK-004). Ejecuta `make` para ver la ayuda.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

ENV_FILE     ?= .env
COMPOSE_FILE := infra/docker-compose.yml
COMPOSE      := docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE)

# Puertos publicados, leídos de $(ENV_FILE) solo para mostrar las URLs.
env_value = $(or $(shell grep -E '^$(1)=' $(ENV_FILE) 2>/dev/null | tail -1 | cut -d= -f2 | cut -d' ' -f1),$(2))

.PHONY: help check-env build-frontend build-backend build dev migrate clean \
        ci-api ci-web shellcheck \
        tf-bootstrap tf-init tf-plan tf-apply tf-output tf-lint

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

check-env:
	@test -f $(ENV_FILE) || { echo "Falta $(ENV_FILE); copia .env.example: cp .env.example $(ENV_FILE)" >&2; exit 1; }

build-frontend: check-env ## Construye la imagen del servicio web
	$(COMPOSE) build web

build-backend: check-env ## Construye la imagen del servicio api
	$(COMPOSE) build api

build: build-frontend build-backend ## Construye las imágenes de web y api

dev: build ## Construye las imágenes, levanta db, mail, api y web y aplica las migraciones
	$(COMPOSE) up -d db mail api web
	$(COMPOSE) exec -T api alembic upgrade head
	@echo "web: http://localhost:$(call env_value,WEB_PORT,3000)"
	@echo "api: http://localhost:$(call env_value,API_PORT,8000)/docs"
	@echo "correo: http://localhost:$(call env_value,MAIL_UI_HOST_PORT,8025)"

migrate: check-env ## Aplica las migraciones pendientes de la base de datos
	$(COMPOSE) run --rm api alembic upgrade head

clean: check-env ## Elimina contenedores e imágenes locales (conserva los volúmenes de datos)
	$(COMPOSE) down --rmi local --remove-orphans

# --- Comprobaciones de AGENTS.md, las mismas en local y en CI (TK-089) ---

ci-api: check-env ## Lint, formato y pruebas de la API (incluidas las de base de datos)
	$(COMPOSE) build api
	$(COMPOSE) run --rm api ruff check .
	$(COMPOSE) run --rm api ruff format --check .
	$(COMPOSE) run --rm -v "$(CURDIR)/apps/api/tests:/app/tests" api python -m pytest -q

# Sobre la imagen `dev`, sin montar el código: en CI el usuario del runner no es el de la imagen.
ci-web: ## Lint, tipos y pruebas de la web
	docker build --target dev -t entrevecinos-web-ci apps/web
	docker run --rm entrevecinos-web-ci npm run lint
	docker run --rm entrevecinos-web-ci npm run typecheck
	docker run --rm entrevecinos-web-ci npm run test

SHELLCHECK_IMAGE := koalaman/shellcheck:v0.11.0

shellcheck: ## shellcheck de los scripts de producción (infra/prod)
	docker run --rm -v "$(CURDIR):/mnt:ro" -w /mnt $(SHELLCHECK_IMAGE) $(wildcard infra/prod/*.sh infra/prod/*/*.sh)

# --- Producción en AWS (TK-078). Terraform y sus linters se ejecutan en contenedores. ---
# Las credenciales temporales de `aws login` se pasan al contenedor por entorno, sin escribirlas
# en disco. Guía: infra/aws/README.md.

AWS_PROFILE     ?= entrevecinos
TF_IMAGE        := hashicorp/terraform:1.16.7
TFLINT_IMAGE    := ghcr.io/terraform-linters/tflint:v0.65.0
CHECKOV_IMAGE   := bridgecrew/checkov:3.3.30
TF_ENV_DIR      := infra/aws/envs/prod
TF_BOOTSTRAP_DIR := infra/aws/bootstrap
TF_VARS         := prod.tfvars

aws_credentials = <(aws configure export-credentials --profile $(AWS_PROFILE) --format env-no-export)
# -it solo con terminal (en CI o en un shell sin TTY, docker run -t falla).
TTY_FLAGS := $(shell [ -t 0 ] && echo -it || echo -i)
# $(call terraform,<directorio>,<argumentos>)
terraform = docker run --rm $(TTY_FLAGS) -u $$(id -u):$$(id -g) -e HOME=/tmp -e AWS_REGION=eu-north-1 \
	--env-file $(aws_credentials) -v "$(CURDIR)":/work -w /work/$(1) $(TF_IMAGE) $(2)

check-tfvars:
	@test -f $(TF_ENV_DIR)/$(TF_VARS) || { echo "Falta $(TF_ENV_DIR)/$(TF_VARS); copia $(TF_VARS).example" >&2; exit 1; }

tf-bootstrap: ## Crea el bucket del estado de Terraform (una sola vez)
	$(call terraform,$(TF_BOOTSTRAP_DIR),init)
	$(call terraform,$(TF_BOOTSTRAP_DIR),apply)

tf-init: ## Inicializa Terraform de producción con el estado en S3
	$(call terraform,$(TF_ENV_DIR),init)

tf-plan: check-tfvars ## Muestra los cambios de la infraestructura de producción
	$(call terraform,$(TF_ENV_DIR),plan -var-file=$(TF_VARS))

tf-apply: check-tfvars ## Aplica los cambios en producción (pide confirmación)
	$(call terraform,$(TF_ENV_DIR),apply -var-file=$(TF_VARS))

tf-output: ## Muestra las salidas de Terraform de producción
	$(call terraform,$(TF_ENV_DIR),output)

tf-lint: ## Formato, validación, tflint y checkov de infra/aws (sin credenciales)
# Directorio de trabajo aparte (.terraform-lint): no toca el backend S3 ya inicializado.
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -v "$(CURDIR)":/work -w /work/infra/aws $(TF_IMAGE) fmt -check -recursive -diff
	for dir in $(TF_BOOTSTRAP_DIR) $(TF_ENV_DIR); do \
		docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -v "$(CURDIR)":/work -e TF_DATA_DIR=.terraform-lint -w /work/$$dir $(TF_IMAGE) init -backend=false -input=false >/dev/null; \
		docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -v "$(CURDIR)":/work -e TF_DATA_DIR=.terraform-lint -w /work/$$dir $(TF_IMAGE) validate; \
	done
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -e GITHUB_TOKEN -v "$(CURDIR)":/work -w /work/infra/aws --entrypoint sh $(TFLINT_IMAGE) \
		-c "tflint --init --config=/work/infra/aws/.tflint.hcl && tflint --recursive --config=/work/infra/aws/.tflint.hcl"
	docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -v "$(CURDIR)":/work -w /work/infra/aws $(CHECKOV_IMAGE) \
		--directory . --config-file .checkov.yaml
