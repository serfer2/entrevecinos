import uuid
from datetime import datetime

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from entrevecinos.infrastructure.db.base import Base

USER_ROLE = Enum("user", "platform_admin", name="user_role")


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint("length(trim(full_name)) > 0", name="full_name_not_blank"),
        # Una cuenta activa tiene el correo validado, salvo la de un platform_admin.
        CheckConstraint(
            "NOT is_active OR email_verified_at IS NOT NULL OR platform_role = 'platform_admin'",
            name="active_requires_verified_email",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(32))
    avatar_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("media_asset.id", ondelete="SET NULL", use_alter=True)
    )
    platform_role: Mapped[str] = mapped_column(USER_ROLE, server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # statement_timestamp(): now() devolvería el inicio de la transacción, no el del cambio.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.statement_timestamp()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EmailVerificationModel(Base):
    """Enlace de validación del correo. Solo se guarda el SHA-256 del token."""

    __tablename__ = "email_verification"
    __table_args__ = (
        Index(None, "user_id"),
        CheckConstraint("used_at IS NULL OR superseded_at IS NULL", name="used_or_superseded"),
        # Solo vale el último enlace: como mucho uno vigente por usuario (migración 0009).
        Index(
            "uq_email_verification_one_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("used_at IS NULL AND superseded_at IS NULL"),
        ),
    )

    token_hash: Mapped[str] = mapped_column(CHAR(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
