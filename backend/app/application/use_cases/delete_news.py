"""[Feature: News Management] [Story: NM-ADMIN-004] Delete news article use case."""

import logging
from uuid import UUID

from app.domain.ports.repositories import NewsRepository

logger = logging.getLogger(__name__)


class DeleteNewsUseCase:
    """Use case for soft-deleting a news article."""

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def execute(self, article_id: UUID, admin_user_id: UUID) -> bool:
        """
        [Feature: News Management] [Story: NM-ADMIN-004] Execute soft delete article.

        Args:
            article_id: UUID of article to delete.
            admin_user_id: UUID of admin performing the deletion.

        Returns:
            True if article was deleted, False if not found.

        Raises:
            ValueError: If article not found.
        """
        article = await self.repository.get_by_id(article_id, only_published=False)
        if not article:
            raise ValueError(f"Article {article_id} not found")

        # Soft delete
        success = await self.repository.soft_delete(article_id)

        # Log deletion event
        if success:
            logger.info(
                "Article deleted",
                extra={
                    "article_id": str(article_id),
                    "admin_user_id": str(admin_user_id),
                    "action": "DELETE",
                },
            )

        return success
