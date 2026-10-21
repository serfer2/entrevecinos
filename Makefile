# Comandos de desarrollo de EntreVecinos (TK-004). Ejecuta `make` para ver la ayuda.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

ENV_FILE     ?= .env
COMPOSE_FILE := infra/docker-compose.yml
COMPOSE      := docker compose --env-file $(ENV_FILE) -f $(COMPOSE_FILE)

# Puertos publicados, leídos de $(ENV_FILE) solo para mostrar las URLs.
env_value = $(or $(shell grep -E '^$(1)=' $(ENV_FILE) 2>/dev/null | tail -1 | cut -d= -f2 | cut -d' ' -f1),$(2))

.PHONY: help check-env build-frontend build-backend build dev migrate clean

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
