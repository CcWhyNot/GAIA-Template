"""[Feature: News Management] [Story: NM-VISITOR-002] List news articles use case."""

from typing import List, Optional, Tuple

from app.domain.entities.news import NewsArticle, NewsScope, NewsStatus
from app.domain.ports.repositories import NewsRepository


class ListNewsUseCase:
    """Use case for listing news articles with filtering and pagination."""

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        search_query: Optional[str] = None,
        scope_filter: Optional[NewsScope] = None,
        user_role: Optional[str] = None,
    ) -> Tuple[List[NewsArticle], int]:
        """
        [Feature: News Management] [Story: NM-VISITOR-002] Execute list news articles.

        Args:
            skip: Number of articles to skip (pagination offset).
            limit: Maximum articles to return (capped at 100).
            search_query: Optional search query (filters title and summary).
            scope_filter: Optional scope filter (GENERAL or INTERNAL).
            user_role: Role of requesting user (ADMIN, MEMBER, SUPPORTER, VISITOR).

        Returns:
            Tuple of (articles list, total count).
        """
        # Cap limit to prevent DoS
        limit = min(limit, 100)

        # Determine which statuses to include based on user role
        status_filter = None
        if user_role != "ADMIN":
            # Non-admin users only see PUBLISHED articles
            status_filter = NewsStatus.PUBLISHED

        # Query repository with role-based scope filtering
        articles, total_count = await self.repository.list(
            skip=skip,
            limit=limit,
            status=status_filter,
            scope=scope_filter,
            search_query=search_query,
            user_role=user_role,
        )

        return articles, total_count
