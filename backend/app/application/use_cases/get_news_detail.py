"""[Feature: News Management] [Story: NM-MEMBER-001] Get news article detail use case."""

from typing import Optional
from uuid import UUID

from app.domain.entities.news import NewsArticle, NewsScope
from app.domain.ports.repositories import NewsRepository


class GetNewsDetailUseCase:
    """Use case for retrieving a single news article detail."""

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def execute(
        self, article_id: UUID, user_role: Optional[str] = None
    ) -> Optional[NewsArticle]:
        """
        [Feature: News Management] [Story: NM-MEMBER-001] Execute get news detail.

        Args:
            article_id: UUID of article to retrieve.
            user_role: Role of requesting user (ADMIN, MEMBER, SUPPORTER, VISITOR).

        Returns:
            NewsArticle if visible to user, None otherwise (returns 404 to client).

        Note:
            INTERNAL articles are never visible to non-members (returns 404, not 403).
        """
        # Only PUBLISHED articles are visible to non-admin users
        article = await self.repository.get_by_id(article_id, only_published=True)
        if not article:
            return None

        # Check scope-based visibility
        if user_role != "MEMBER" and article.scope == NewsScope.INTERNAL:
            # Non-members cannot see INTERNAL articles
            # Return None (which translates to 404) to avoid information disclosure
            return None

        return article
