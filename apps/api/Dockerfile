# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    PATH=/opt/venv/bin:$PATH \
    ASSETS_DIR=/var/lib/entrevecinos/assets

# Usuario sin privilegios; el directorio de assets le pertenece para que el
# volumen con nombre herede los permisos al inicializarse.
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --home-dir /app --no-create-home app \
    && mkdir -p /app "$ASSETS_DIR" \
    && chown app:app "$ASSETS_DIR"

WORKDIR /app
EXPOSE 8000

# --- Desarrollo: dependencias de dev, paquete editable y recarga automática ---
FROM base AS dev

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project
COPY src ./src
COPY tests ./tests
RUN uv sync --frozen && chown -R app:app /app

USER app
CMD ["uvicorn", "entrevecinos.presentation.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]

# --- Producción: solo dependencias de runtime, sin tests ni recarga ---
FROM base AS prod

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

USER app
CMD ["uvicorn", "entrevecinos.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
