import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from entrevecinos.infrastructure.db.base import Base

USER_ROLE = Enum("user", "platform_admin", name="user_role")


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint("length(trim(full_name)) > 0", name="full_name_not_blank"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(32))
    # FK a media_asset.id pendiente hasta que exista la tabla (TK-005 §2).
    avatar_asset_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    platform_role: Mapped[str] = mapped_column(USER_ROLE, server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # statement_timestamp(): now() devolvería el inicio de la transacción, no el del cambio.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.statement_timestamp()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
