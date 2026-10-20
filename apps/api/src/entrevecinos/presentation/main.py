from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from entrevecinos.infrastructure.settings import Settings, get_settings
from entrevecinos.presentation.errors import register_error_handlers
from entrevecinos.presentation.v1.router import router as v1_router


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="API de EntreVecinos", version="1.0.0")
    if settings is None:
        settings = get_settings()
    else:
        # Las dependencias que leen la configuración usan la recibida (pruebas).
        app.dependency_overrides[get_settings] = lambda: settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(v1_router)
    return app


app = create_app()
