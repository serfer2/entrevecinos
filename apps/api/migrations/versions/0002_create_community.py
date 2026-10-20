"""Crea los enums de membresía y las tablas community y community_membership.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

membership_role = sa.Enum("member", "community_admin", "moderator", name="membership_role")
membership_status = sa.Enum("pending", "approved", "rejected", "blocked", name="membership_status")


def upgrade() -> None:
    op.create_table(
        "community",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("postal_code", sa.String(16), nullable=True),
        sa.Column("city", sa.String(120), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name=op.f("ck_community_name_not_blank")),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk_community_created_by_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_community")),
    )
    op.create_table(
        "community_membership",
        sa.Column("community_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", membership_role, server_default="member", nullable=False),
        sa.Column("status", membership_status, server_default="pending", nullable=False),
        sa.Column("reviewed_by", sa.Uuid(), nullable=True),
        sa.Column(
            "requested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status <> 'approved' OR joined_at IS NOT NULL",
            name=op.f("ck_community_membership_approved_has_joined_at"),
        ),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["community.id"],
            name=op.f("fk_community_membership_community_id_community"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_community_membership_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            name=op.f("fk_community_membership_reviewed_by_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("community_id", "user_id", name=op.f("pk_community_membership")),
    )
    op.create_index(
        op.f("ix_community_membership_user_id_status"),
        "community_membership",
        ["user_id", "status"],
    )
    op.create_index(
        op.f("ix_community_membership_community_id_status"),
        "community_membership",
        ["community_id", "status"],
    )


def downgrade() -> None:
    op.drop_table("community_membership")
    op.drop_table("community")
    membership_status.drop(op.get_bind(), checkfirst=True)
    membership_role.drop(op.get_bind(), checkfirst=True)
