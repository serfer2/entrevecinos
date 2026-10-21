"""Validación del correo: users.email_verified_at, su restricción y la tabla email_verification.

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True)))
    # Hasta ahora las cuentas se activaban al registrarse: se dan por validadas.
    op.execute("UPDATE users SET email_verified_at = created_at")
    op.create_check_constraint(
        op.f("ck_users_active_requires_verified_email"),
        "users",
        "NOT is_active OR email_verified_at IS NOT NULL OR platform_role = 'platform_admin'",
    )

    op.create_table(
        "email_verification",
        sa.Column("token_hash", sa.CHAR(64), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_email_verification_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_hash", name=op.f("pk_email_verification")),
    )
    op.create_index(
        op.f("ix_email_verification_user_id"), "email_verification", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_email_verification_user_id"), table_name="email_verification")
    op.drop_table("email_verification")
    op.drop_constraint(op.f("ck_users_active_requires_verified_email"), "users", type_="check")
    op.drop_column("users", "email_verified_at")
