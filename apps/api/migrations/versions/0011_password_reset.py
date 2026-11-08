"""Recuperación de la contraseña (TK-100): tabla password_reset y users.password_changed_at.

Revision ID: 0011
Revises: 0010
Create Date: 2026-11-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nula en las cuentas existentes: sus sesiones siguen valiendo.
    op.add_column("users", sa.Column("password_changed_at", sa.DateTime(timezone=True)))

    op.create_table(
        "password_reset",
        sa.Column("token_hash", sa.CHAR(64), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_password_reset_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_hash", name=op.f("pk_password_reset")),
    )
    op.create_index(op.f("ix_password_reset_user_id"), "password_reset", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_password_reset_user_id"), table_name="password_reset")
    op.drop_table("password_reset")
    op.drop_column("users", "password_changed_at")
