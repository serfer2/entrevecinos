from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API leída de variables de entorno."""

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str
    cors_origins: str = "http://localhost:3000"
    environment: Literal["development", "production"] = "development"
    jwt_secret: str = Field(min_length=32)
    jwt_ttl_seconds: int = Field(default=86400, gt=0)
    storage_endpoint: str
    # Base de las URL prefirmadas: el host que abre el navegador (la firma lo incluye).
    storage_public_endpoint: str
    storage_bucket: str
    storage_access_key: str
    storage_secret_key: str
    media_max_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    media_url_ttl_seconds: int = Field(default=300, gt=30)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
