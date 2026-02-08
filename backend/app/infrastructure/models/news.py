"""[Feature: News Management] [Story: NM-ADMIN-001] SQLAlchemy models for news articles."""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.domain.entities.news import NewsScope, NewsStatus


class NewsArticleModel(Base):
    """SQLAlchemy ORM model for news_articles table."""

    __tablename__ = "news_articles"

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    title = Column(String(255), nullable=False, index=True)
    summary = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(
        Enum(NewsStatus),
        nullable=False,
        default=NewsStatus.DRAFT,
        index=True,
    )
    scope = Column(
        Enum(NewsScope),
        nullable=False,
        index=True,
    )
    author_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    cover_url = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=False, default=list)
    published_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    def __repr__(self):
        return f"<NewsArticleModel(id={self.id}, title={self.title}, status={self.status})>"

    def to_domain(self):
        """Convert SQLAlchemy model to domain entity."""
        from app.domain.entities.news import NewsArticle

        return NewsArticle(
            id=self.id,
            title=self.title,
            summary=self.summary,
            content=self.content,
            status=self.status,
            scope=self.scope,
            author_id=self.author_id,
            cover_url=self.cover_url,
            tags=self.tags or [],
            published_at=self.published_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
            is_deleted=self.is_deleted,
        )
