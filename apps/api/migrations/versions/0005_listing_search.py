"""Búsqueda de texto completo en anuncios: configuración es_unaccent, columna e índice GIN.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-20
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Español sin distinguir tildes: unaccent (migración 0003) antes del stemmer.
    op.execute("CREATE TEXT SEARCH CONFIGURATION es_unaccent (COPY = spanish)")
    op.execute(
        "ALTER TEXT SEARCH CONFIGURATION es_unaccent "
        "ALTER MAPPING FOR hword, hword_part, word WITH unaccent, spanish_stem"
    )
    op.execute(
        """
        ALTER TABLE listing ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (
          setweight(to_tsvector('es_unaccent', coalesce(title, '')), 'A') ||
          setweight(to_tsvector('es_unaccent', coalesce(description, '')), 'B')
        ) STORED
        """
    )
    op.execute("CREATE INDEX ix_listing_search_vector ON listing USING GIN (search_vector)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_listing_search_vector")
    op.execute("ALTER TABLE listing DROP COLUMN IF EXISTS search_vector")
    op.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS es_unaccent")
