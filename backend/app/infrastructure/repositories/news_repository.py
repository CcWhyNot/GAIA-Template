"""[Feature: News Management] [Story: NM-ADMIN-001] Repository implementation for news articles."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.domain.entities.news import NewsArticle, NewsScope, NewsStatus
from app.domain.ports.repositories import NewsRepository
from app.infrastructure.models.news import NewsArticleModel


class SQLAlchemyNewsRepository(NewsRepository):
    """SQLAlchemy implementation of NewsRepository."""

    def __init__(self, db: Session):
        self.db = db

    async def save(self, article: NewsArticle) -> NewsArticle:
        """[Feature: News Management] [Story: NM-ADMIN-001] Save a new news article."""
        db_article = NewsArticleModel(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            status=article.status,
            scope=article.scope,
            author_id=article.author_id,
            cover_url=article.cover_url,
            tags=article.tags,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            is_deleted=article.is_deleted,
        )
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article.to_domain()

    async def get_by_id(
        self, article_id: UUID, only_published: bool = False
    ) -> Optional[NewsArticle]:
        """[Feature: News Management] [Story: NM-MEMBER-001] Get article by ID."""
        query = self.db.query(NewsArticleModel).filter(
            NewsArticleModel.id == article_id,
            NewsArticleModel.is_deleted == False,
        )

        if only_published:
            query = query.filter(NewsArticleModel.status == NewsStatus.PUBLISHED)

        db_article = query.first()
        return db_article.to_domain() if db_article else None

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[NewsStatus] = None,
        scope: Optional[NewsScope] = None,
        search_query: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> tuple[List[NewsArticle], int]:
        """[Feature: News Management] [Story: NM-VISITOR-002] List articles with filtering."""
        # Cap limit to prevent DoS
        limit = min(limit, 100)

        # Base query: always exclude soft-deleted
        query = self.db.query(NewsArticleModel).filter(
            NewsArticleModel.is_deleted == False
        )

        # Role-based scope filtering
        if user_role != "ADMIN":
            if user_role == "MEMBER":
                # Members see GENERAL and INTERNAL
                scope_filter = None  # No restriction
            else:
                # Visitors and Supporters see only GENERAL
                query = query.filter(NewsArticleModel.scope == NewsScope.GENERAL)

            # Non-admin users only see PUBLISHED articles
            query = query.filter(NewsArticleModel.status == NewsStatus.PUBLISHED)
        else:
            # Admins see all statuses
            pass

        # Apply explicit scope filter if provided (Members can filter by scope)
        if scope is not None:
            query = query.filter(NewsArticleModel.scope == scope)

        # Apply explicit status filter if provided
        if status is not None:
            query = query.filter(NewsArticleModel.status == status)

        # Search by title or summary
        if search_query:
            search_filter = or_(
                NewsArticleModel.title.ilike(f"%{search_query}%"),
                NewsArticleModel.summary.ilike(f"%{search_query}%"),
            )
            query = query.filter(search_filter)

        # Get total count before pagination
        total_count = query.count()

        # Sort by published_at DESC (most recent first)
        # For drafts, use updated_at DESC
        query = query.order_by(NewsArticleModel.published_at.desc().nullslast())

        # Pagination
        articles = query.offset(skip).limit(limit).all()

        return [article.to_domain() for article in articles], total_count

    async def soft_delete(self, article_id: UUID) -> bool:
        """[Feature: News Management] [Story: NM-ADMIN-004] Soft delete an article."""
        article = await self.get_by_id(article_id, only_published=False)
        if not article:
            return False

        self.db.query(NewsArticleModel).filter(
            NewsArticleModel.id == article_id
        ).update({NewsArticleModel.is_deleted: True})
        self.db.commit()
        return True

    async def update(self, article: NewsArticle) -> NewsArticle:
        """[Feature: News Management] [Story: NM-ADMIN-002] Update an existing article."""
        db_article = (
            self.db.query(NewsArticleModel)
            .filter(NewsArticleModel.id == article.id)
            .first()
        )

        if not db_article:
            raise ValueError(f"Article {article.id} not found")

        db_article.title = article.title
        db_article.summary = article.summary
        db_article.content = article.content
        db_article.scope = article.scope
        db_article.status = article.status
        db_article.cover_url = article.cover_url
        db_article.tags = article.tags
        db_article.published_at = article.published_at
        db_article.updated_at = article.updated_at
        db_article.is_deleted = article.is_deleted

        self.db.commit()
        self.db.refresh(db_article)
        return db_article.to_domain()
