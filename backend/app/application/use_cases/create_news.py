"""[Feature: News Management] [Story: NM-ADMIN-001] Create news article use case."""

from uuid import UUID

from app.core.sanitizers import sanitize_html

from app.domain.entities.news import NewsArticle, NewsScope
from app.domain.ports.repositories import NewsRepository


class CreateNewsUseCase:
    """Use case for creating a new news article."""

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def execute(
        self,
        title: str,
        summary: str,
        content: str,
        scope: NewsScope,
        author_id: UUID,
        cover_url: str = None,
        tags: list[str] = None,
    ) -> NewsArticle:
        """
        [Feature: News Management] [Story: NM-ADMIN-001] Execute create news article.

        Args:
            title: Article title.
            summary: Article summary.
            content: Article HTML content (will be sanitized).
            scope: Visibility scope (GENERAL or INTERNAL).
            author_id: UUID of the author.
            cover_url: Optional cover image URL.
            tags: Optional list of tags.

        Returns:
            Created NewsArticle entity.
        """
        # Sanitize HTML content to prevent XSS
        sanitized_content = sanitize_html(content)

        # Create domain entity
        article = NewsArticle(
            title=title,
            summary=summary,
            content=sanitized_content,
            scope=scope,
            author_id=author_id,
            cover_url=cover_url,
            tags=tags or [],
        )

        # Persist
        saved_article = await self.repository.save(article)
        return saved_article
