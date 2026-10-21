"""Una sola comunidad pendiente de aprobación (inactiva) por creador.

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_community_one_pending_per_creator",
        "community",
        ["created_by"],
        unique=True,
        postgresql_where=sa.text("NOT is_active"),
    )


def downgrade() -> None:
    op.drop_index("uq_community_one_pending_per_creator", table_name="community")
