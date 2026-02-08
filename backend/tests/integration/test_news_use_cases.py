"""[Feature: News Management] Integration tests for news use cases."""

import asyncio
from uuid import uuid4

import pytest

from app.application.use_cases.change_news_status import ChangeNewsStatusUseCase
from app.application.use_cases.create_news import CreateNewsUseCase
from app.application.use_cases.delete_news import DeleteNewsUseCase
from app.application.use_cases.get_news_detail import GetNewsDetailUseCase
from app.application.use_cases.list_news import ListNewsUseCase
from app.application.use_cases.update_news import UpdateNewsUseCase
from app.domain.entities.news import NewsScope, NewsStatus


class TestCreateNewsUseCase:
    """[Feature: News Management] [Story: NM-ADMIN-001] Test creating news articles."""

    @pytest.mark.asyncio
    async def test_create_article(self, repository, admin_user, sample_article_data):
        """Test creating a news article."""
        use_case = CreateNewsUseCase(repository)

        article = await use_case.execute(**sample_article_data)

        assert article.title == sample_article_data["title"]
        assert article.status == NewsStatus.DRAFT
        assert article.author_id == admin_user.user_id

    @pytest.mark.asyncio
    async def test_xss_content_sanitized(self, repository, admin_user):
        """[Feature: News Management] [Story: NM-ADMIN-001] Test that XSS content is sanitized."""
        use_case = CreateNewsUseCase(repository)

        article = await use_case.execute(
            title="XSS Test",
            summary="Summary",
            content="<script>alert('xss')</script><p>Safe</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        assert "<script>" not in article.content
        assert "<p>Safe</p>" in article.content


class TestChangeNewsStatusUseCase:
    """[Feature: News Management] [Story: NM-ADMIN-003] Test changing article status."""

    @pytest.mark.asyncio
    async def test_publish_draft_article(self, repository, admin_user):
        """Test publishing a draft article."""
        # Create article
        create_use_case = CreateNewsUseCase(repository)
        article = await create_use_case.execute(
            title="Test",
            summary="Summary",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        # Publish it
        change_use_case = ChangeNewsStatusUseCase(repository)
        published = await change_use_case.execute(
            article_id=article.id,
            target_status=NewsStatus.PUBLISHED,
        )

        assert published.status == NewsStatus.PUBLISHED
        assert published.published_at is not None

    @pytest.mark.asyncio
    async def test_invalid_transition_rejected(self, repository, admin_user):
        """Test that invalid status transitions are rejected."""
        # Create article
        create_use_case = CreateNewsUseCase(repository)
        article = await create_use_case.execute(
            title="Test",
            summary="Summary",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        # Try to archive without publishing (invalid)
        change_use_case = ChangeNewsStatusUseCase(repository)
        with pytest.raises(ValueError):
            await change_use_case.execute(
                article_id=article.id,
                target_status=NewsStatus.ARCHIVED,
            )


class TestGetNewsDetailUseCase:
    """[Feature: News Management] [Story: NM-MEMBER-001] Test viewing article details."""

    @pytest.mark.asyncio
    async def test_member_views_general_article(
        self, repository, admin_user, member_user
    ):
        """Test that members can view GENERAL articles."""
        # Create and publish article
        create_use_case = CreateNewsUseCase(repository)
        article = await create_use_case.execute(
            title="Test",
            summary="Summary",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        change_use_case = ChangeNewsStatusUseCase(repository)
        await change_use_case.execute(
            article_id=article.id,
            target_status=NewsStatus.PUBLISHED,
        )

        # Member views it
        get_use_case = GetNewsDetailUseCase(repository)
        retrieved = await get_use_case.execute(
            article_id=article.id,
            user_role=member_user.role,
        )

        assert retrieved is not None
        assert retrieved.id == article.id

    @pytest.mark.asyncio
    async def test_visitor_cannot_view_internal(
        self, repository, admin_user, visitor_user
    ):
        """Test that visitors cannot view INTERNAL articles."""
        # Create and publish INTERNAL article
        create_use_case = CreateNewsUseCase(repository)
        article = await create_use_case.execute(
            title="Internal News",
            summary="Summary",
            content="<p>Content</p>",
            scope=NewsScope.INTERNAL,
            author_id=admin_user.user_id,
        )

        change_use_case = ChangeNewsStatusUseCase(repository)
        await change_use_case.execute(
            article_id=article.id,
            target_status=NewsStatus.PUBLISHED,
        )

        # Visitor tries to view (should get None/404)
        get_use_case = GetNewsDetailUseCase(repository)
        retrieved = await get_use_case.execute(
            article_id=article.id,
            user_role=visitor_user.role,
        )

        assert retrieved is None


class TestListNewsUseCase:
    """[Feature: News Management] [Story: NM-VISITOR-002] Test listing articles."""

    @pytest.mark.asyncio
    async def test_list_general_articles(self, repository, admin_user, visitor_user):
        """Test listing GENERAL articles for visitors."""
        # Create and publish articles
        create_use_case = CreateNewsUseCase(repository)
        article1 = await create_use_case.execute(
            title="Article 1",
            summary="Summary 1",
            content="<p>Content 1</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        article2 = await create_use_case.execute(
            title="Article 2",
            summary="Summary 2",
            content="<p>Content 2</p>",
            scope=NewsScope.INTERNAL,
            author_id=admin_user.user_id,
        )

        change_use_case = ChangeNewsStatusUseCase(repository)
        await change_use_case.execute(
            article_id=article1.id,
            target_status=NewsStatus.PUBLISHED,
        )
        await change_use_case.execute(
            article_id=article2.id,
            target_status=NewsStatus.PUBLISHED,
        )

        # Visitor lists articles
        list_use_case = ListNewsUseCase(repository)
        articles, total = await list_use_case.execute(
            user_role=visitor_user.role,
        )

        # Should only see GENERAL article
        assert len(articles) == 1
        assert articles[0].scope == NewsScope.GENERAL
        assert total == 1

    @pytest.mark.asyncio
    async def test_search_articles(self, repository, admin_user):
        """Test searching articles by title."""
        create_use_case = CreateNewsUseCase(repository)

        # Create multiple articles
        article1 = await create_use_case.execute(
            title="Fiesta del Barrio",
            summary="Party",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        article2 = await create_use_case.execute(
            title="Obras en la Calle",
            summary="Works",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=admin_user.user_id,
        )

        # Publish both
        change_use_case = ChangeNewsStatusUseCase(repository)
        await change_use_case.execute(
            article_id=article1.id,
            target_status=NewsStatus.PUBLISHED,
        )
        await change_use_case.execute(
            article_id=article2.id,
            target_status=NewsStatus.PUBLISHED,
        )

        # Search for "Fiesta"
        list_use_case = ListNewsUseCase(repository)
        articles, total = await list_use_case.execute(
            search_query="Fiesta",
            user_role="VISITOR",
        )

        assert len(articles) == 1
        assert "Fiesta" in articles[0].title
