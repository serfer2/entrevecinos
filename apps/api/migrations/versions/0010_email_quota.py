"""Cupo de correos por periodo (TK-099): tabla email_quota, una fila por periodo.

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "email_quota",
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("sent", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("sent >= 0", name=op.f("ck_email_quota_sent_not_negative")),
        sa.PrimaryKeyConstraint("period_start", name=op.f("pk_email_quota")),
    )


def downgrade() -> None:
    op.drop_table("email_quota")
