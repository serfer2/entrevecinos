"""Activa unaccent y crea f_unaccent(text), una versión inmutable e indexable.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-20
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    # unaccent() es STABLE (depende del search_path); fijar el diccionario la hace inmutable.
    op.execute(
        """
        CREATE FUNCTION f_unaccent(text) RETURNS text
        LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT
        AS $$ SELECT public.unaccent('public.unaccent'::regdictionary, $1) $$
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS f_unaccent(text)")
    op.execute("DROP EXTENSION IF EXISTS unaccent")
