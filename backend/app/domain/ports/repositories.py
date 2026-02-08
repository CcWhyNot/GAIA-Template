"""Repository ports (interfaces) for the domain layer."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.news import NewsArticle, NewsScope, NewsStatus


class NewsRepository(ABC):
    """[Feature: News Management] [Story: NM-ADMIN-001] Repository interface for news articles."""

    @abstractmethod
    async def save(self, article: NewsArticle) -> NewsArticle:
        """Save a new or updated news article."""
        pass

    @abstractmethod
    async def get_by_id(
        self, article_id: UUID, only_published: bool = False
    ) -> Optional[NewsArticle]:
        """
        Get article by ID.

        Args:
            article_id: UUID of the article.
            only_published: If True, only return PUBLISHED articles (exclude DRAFT/ARCHIVED).

        Returns:
            NewsArticle if found and not soft-deleted, None otherwise.
        """
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[NewsStatus] = None,
        scope: Optional[NewsScope] = None,
        search_query: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> tuple[List[NewsArticle], int]:
        """
        List articles with filtering and pagination.

        Args:
            skip: Number of articles to skip (pagination offset).
            limit: Maximum number of articles to return.
            status: Filter by status (DRAFT, PUBLISHED, ARCHIVED).
            scope: Filter by scope (GENERAL, INTERNAL).
            search_query: Search in title and summary (case-insensitive).
            user_role: User role for scope-based filtering (ADMIN, MEMBER, SUPPORTER, VISITOR).

        Returns:
            Tuple of (articles list, total count).
        """
        pass

    @abstractmethod
    async def soft_delete(self, article_id: UUID) -> bool:
        """
        Soft delete an article (set is_deleted=true).

        Returns:
            True if article was deleted, False if already deleted or not found.
        """
        pass

    @abstractmethod
    async def update(self, article: NewsArticle) -> NewsArticle:
        """Update an existing article."""
        pass
