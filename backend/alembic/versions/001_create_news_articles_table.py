"""[Feature: News Management] [Story: NM-ADMIN-001] Create news_articles table

Revision ID: 001
Revises:
Create Date: 2026-02-08 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """[Feature: News Management] [Story: NM-ADMIN-001] Create news_articles table."""
    # Create ENUM types
    news_status = postgresql.ENUM(
        "DRAFT", "PUBLISHED", "ARCHIVED", name="news_status", create_type=True
    )
    news_scope = postgresql.ENUM(
        "GENERAL", "INTERNAL", name="news_scope", create_type=True
    )

    # Create table
    op.create_table(
        "news_articles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", news_status, nullable=False, server_default="DRAFT"),
        sa.Column("scope", news_scope, nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cover_url", sa.String(), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_news_articles_status", "news_articles", ["status"])
    op.create_index("ix_news_articles_scope", "news_articles", ["scope"])
    op.create_index("ix_news_articles_published_at", "news_articles", ["published_at"])
    op.create_index("ix_news_articles_is_deleted", "news_articles", ["is_deleted"])
    op.create_index(
        "ix_news_articles_composite",
        "news_articles",
        ["scope", "status", "is_deleted", "published_at"],
    )
    op.create_index("ix_news_articles_author_id", "news_articles", ["author_id"])
    op.create_index("ix_news_articles_title", "news_articles", ["title"])


def downgrade() -> None:
    """Drop news_articles table."""
    op.drop_table("news_articles")
    op.execute("DROP TYPE IF EXISTS news_status")
    op.execute("DROP TYPE IF EXISTS news_scope")
