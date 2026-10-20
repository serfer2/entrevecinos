"""Auditoría mínima de la retirada de anuncios: quién y cuándo (hidden_by, hidden_at).

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("listing", sa.Column("hidden_by", sa.Uuid(), nullable=True))
    op.add_column("listing", sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        op.f("fk_listing_hidden_by_users"),
        "listing",
        "users",
        ["hidden_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_listing_hidden_by_users"), "listing", type_="foreignkey")
    op.drop_column("listing", "hidden_at")
    op.drop_column("listing", "hidden_by")
