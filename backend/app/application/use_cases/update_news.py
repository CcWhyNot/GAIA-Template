"""[Feature: News Management] [Story: NM-ADMIN-002] Update news article use case."""

from typing import Optional
from uuid import UUID

from app.core.sanitizers import sanitize_html

from app.domain.entities.news import NewsArticle, NewsScope
from app.domain.ports.repositories import NewsRepository


class UpdateNewsUseCase:
    """Use case for updating an existing news article."""

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def execute(
        self,
        article_id: UUID,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        scope: Optional[NewsScope] = None,
        cover_url: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> NewsArticle:
        """
        [Feature: News Management] [Story: NM-ADMIN-002] Execute update news article.

        Args:
            article_id: UUID of article to update.
            title: New title (optional).
            summary: New summary (optional).
            content: New HTML content (will be sanitized) (optional).
            scope: New scope (optional).
            cover_url: New cover URL (optional).
            tags: New tags list (optional).

        Returns:
            Updated NewsArticle entity.

        Raises:
            ValueError: If article not found.
        """
        article = await self.repository.get_by_id(article_id, only_published=False)
        if not article:
            raise ValueError(f"Article {article_id} not found")

        # Update fields
        if title is not None:
            article.title = title
        if summary is not None:
            article.summary = summary
        if content is not None:
            article.content = sanitize_html(content)
        if scope is not None:
            article.scope = scope
        if cover_url is not None:
            article.cover_url = cover_url
        if tags is not None:
            article.tags = tags

        # Persist
        updated_article = await self.repository.update(article)
        return updated_article
