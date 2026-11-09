from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API leída de variables de entorno."""

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str
    cors_origins: str = "http://localhost:3000"
    environment: Literal["development", "production"] = "development"
    jwt_secret: str = Field(min_length=32)
    jwt_ttl_seconds: int = Field(default=86400, gt=0)
    # Vacíos en AWS: endpoint de la región y credenciales del rol de la instancia (TK-081).
    storage_endpoint: str = ""
    # Base de las URL prefirmadas: el host que abre el navegador (la firma lo incluye).
    storage_public_endpoint: str = ""
    storage_bucket: str
    storage_access_key: str = ""
    storage_secret_key: str = ""
    # MinIO ignora la región; en AWS es la del bucket. MinIO necesita direccionamiento `path`.
    storage_region: str = "us-east-1"
    storage_addressing_style: str = "path"
    media_max_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    media_url_ttl_seconds: int = Field(default=300, gt=30)
    # `smtp` (Mailpit en local, Brevo en producción) o `ses` (API de SES con el rol de la instancia,
    # configurada en AWS como vuelta atrás).
    mail_backend: str = "smtp"
    smtp_host: str = ""
    smtp_port: int = Field(default=587, gt=0, lt=65536)
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    ses_region: str = "eu-north-1"
    ses_configuration_set: str = ""
    mail_from: str = Field(min_length=1)
    # Origen de los enlaces que se envían por correo: la web que abre el usuario.
    web_public_url: str = Field(min_length=1)
    email_verification_ttl_hours: int = Field(default=24, gt=0)
    # Enlace para restablecer la contraseña (TK-101): corto, porque da acceso a la cuenta.
    password_reset_ttl_minutes: int = Field(default=60, gt=0)
    # Cupo de correos por periodo (TK-099), por coste: no superar el plan más barato del
    # proveedor (5.000 al mes en Brevo) ni el límite de gasto. El periodo empieza ese día del mes.
    email_monthly_limit: int = Field(default=5000, gt=0)
    email_quota_reset_day: int = Field(default=6, ge=1, le=28)

    @field_validator("storage_addressing_style")
    @classmethod
    def known_addressing_style(cls, value: str) -> str:
        if value not in ("path", "virtual"):
            raise ValueError("STORAGE_ADDRESSING_STYLE debe ser «path» o «virtual».")
        return value

    @field_validator("mail_backend")
    @classmethod
    def known_mail_backend(cls, value: str) -> str:
        if value not in ("smtp", "ses"):
            raise ValueError("MAIL_BACKEND debe ser «smtp» o «ses».")
        return value

    @model_validator(mode="after")
    def storage_keys_together(self) -> "Settings":
        if bool(self.storage_access_key) != bool(self.storage_secret_key):
            raise ValueError(
                "STORAGE_ACCESS_KEY y STORAGE_SECRET_KEY se definen las dos o ninguna "
                "(sin claves se usan las credenciales del rol de AWS)."
            )
        return self

    @model_validator(mode="after")
    def smtp_host_when_smtp(self) -> "Settings":
        if self.mail_backend == "smtp" and not self.smtp_host:
            raise ValueError("Con MAIL_BACKEND=smtp hay que definir SMTP_HOST (smtp_host).")
        return self

    @model_validator(mode="after")
    def secure_mail_in_production(self) -> "Settings":
        if self.environment == "production":
            if self.mail_backend == "smtp" and not self.smtp_starttls:
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
