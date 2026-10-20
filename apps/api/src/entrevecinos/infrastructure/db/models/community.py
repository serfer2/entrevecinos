import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from entrevecinos.infrastructure.db.base import Base

MEMBERSHIP_ROLE = Enum("member", "community_admin", "moderator", name="membership_role")
MEMBERSHIP_STATUS = Enum("pending", "approved", "rejected", "blocked", name="membership_status")


class CommunityModel(Base):
    __tablename__ = "community"
    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="name_not_blank"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    # El nombre no es único: puede repetirse en ciudades distintas.
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    postal_code: Mapped[str | None] = mapped_column(String(16))
    city: Mapped[str | None] = mapped_column(String(120))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.statement_timestamp()
    )


class CommunityMembershipModel(Base):
    __tablename__ = "community_membership"
    __table_args__ = (
        CheckConstraint(
            "status <> 'approved' OR joined_at IS NOT NULL", name="approved_has_joined_at"
        ),
        Index(None, "user_id", "status"),
        Index(None, "community_id", "status"),
    )

    community_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("community.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(MEMBERSHIP_ROLE, server_default="member")
    status: Mapped[str] = mapped_column(MEMBERSHIP_STATUS, server_default="pending")
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
