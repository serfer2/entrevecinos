from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API leída de variables de entorno."""

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str
    assets_dir: str = "/var/lib/entrevecinos/assets"
    cors_origins: str = "http://localhost:3000"
    environment: Literal["development", "production"] = "development"
    jwt_secret: str = Field(min_length=32)
    jwt_ttl_seconds: int = Field(default=86400, gt=0)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
