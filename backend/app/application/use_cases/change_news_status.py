"""[Feature: News Management] [Story: NM-ADMIN-003] Change news article status use case."""

from datetime import datetime
from uuid import UUID

from app.domain.entities.news import NewsArticle, NewsStatus
from app.domain.ports.repositories import NewsRepository


class ChangeNewsStatusUseCase:
    """Use case for changing a news article's status."""

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def execute(self, article_id: UUID, target_status: NewsStatus) -> NewsArticle:
        """
        [Feature: News Management] [Story: NM-ADMIN-003] Execute change article status.

        Args:
            article_id: UUID of article to update.
            target_status: Target status (PUBLISHED or ARCHIVED).

        Returns:
            Updated NewsArticle entity.

        Raises:
            ValueError: If article not found or invalid transition.
        """
        article = await self.repository.get_by_id(article_id, only_published=False)
        if not article:
            raise ValueError(f"Article {article_id} not found")

        # Validate transition
        if not article.can_transition_to(target_status):
            raise ValueError(
                f"Cannot transition from {article.status} to {target_status}"
            )

        # Apply transition
        if target_status == NewsStatus.PUBLISHED:
            article.publish()
        elif target_status == NewsStatus.ARCHIVED:
            article.archive()

        # Persist
        updated_article = await self.repository.update(article)
        return updated_article
