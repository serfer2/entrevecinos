"""Enlaces de validación usados y sustituidos: email_verification.used_at y superseded_at.

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("email_verification", sa.Column("used_at", sa.DateTime(timezone=True)))
    op.add_column("email_verification", sa.Column("superseded_at", sa.DateTime(timezone=True)))
    op.create_check_constraint(
        op.f("ck_email_verification_used_or_superseded"),
        "email_verification",
        "used_at IS NULL OR superseded_at IS NULL",
    )
    # Hasta ahora sustituir un enlace borraba los anteriores: hay como mucho uno por usuario.
    op.create_index(
        "uq_email_verification_one_active_per_user",
        "email_verification",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("used_at IS NULL AND superseded_at IS NULL"),
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM email_verification WHERE used_at IS NOT NULL OR superseded_at IS NOT NULL"
    )
    op.drop_index("uq_email_verification_one_active_per_user", table_name="email_verification")
    op.drop_constraint(
        op.f("ck_email_verification_used_or_superseded"), "email_verification", type_="check"
    )
    op.drop_column("email_verification", "superseded_at")
    op.drop_column("email_verification", "used_at")
