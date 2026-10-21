from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
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
    smtp_host: str = Field(min_length=1)
    smtp_port: int = Field(default=587, gt=0, lt=65536)
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    mail_from: str = Field(min_length=1)
    # Origen de los enlaces que se envían por correo: la web que abre el usuario.
    web_public_url: str = Field(min_length=1)
    email_verification_ttl_hours: int = Field(default=24, gt=0)

    @model_validator(mode="after")
    def secure_mail_in_production(self) -> "Settings":
        if self.environment == "production":
            if not self.smtp_starttls:
                raise ValueError("En producción, SMTP_STARTTLS debe ser true.")
            if not self.web_public_url.startswith("https://"):
                raise ValueError("En producción, WEB_PUBLIC_URL debe usar https.")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
