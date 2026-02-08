"""[Feature: News Management] [Story: NM-ADMIN-001] Unit tests for NewsArticle domain entity."""

from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.entities.news import NewsArticle, NewsScope, NewsStatus


class TestNewsArticle:
    """Test cases for NewsArticle domain entity."""

    def test_create_news_article(self):
        """[Feature: News Management] [Story: NM-ADMIN-001] Test creating a news article."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test Article",
            summary="Test Summary",
            content="<p>Test Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        assert article.title == "Test Article"
        assert article.summary == "Test Summary"
        assert article.scope == NewsScope.GENERAL
        assert article.status == NewsStatus.DRAFT
        assert article.is_deleted is False
        assert article.published_at is None

    def test_publish_article(self):
        """[Feature: News Management] [Story: NM-ADMIN-003] Test publishing an article."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test Article",
            summary="Test Summary",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        article.publish()

        assert article.status == NewsStatus.PUBLISHED
        assert article.published_at is not None

    def test_cannot_publish_already_published(self):
        """Test that published articles cannot be published again."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test",
            summary="Test",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        article.publish()

        with pytest.raises(ValueError):
            article.publish()

    def test_archive_article(self):
        """[Feature: News Management] [Story: NM-ADMIN-003] Test archiving an article."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test",
            summary="Test",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        article.publish()
        article.archive()

        assert article.status == NewsStatus.ARCHIVED

    def test_cannot_archive_draft(self):
        """Test that draft articles cannot be archived directly."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test",
            summary="Test",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        with pytest.raises(ValueError):
            article.archive()

    def test_soft_delete(self):
        """[Feature: News Management] [Story: NM-ADMIN-004] Test soft deleting an article."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test",
            summary="Test",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        article.soft_delete()

        assert article.is_deleted is True

    def test_valid_transitions(self):
        """[Feature: News Management] [Story: NM-ADMIN-003] Test valid state transitions."""
        author_id = uuid4()
        article = NewsArticle(
            title="Test",
            summary="Test",
            content="<p>Content</p>",
            scope=NewsScope.GENERAL,
            author_id=author_id,
        )

        # DRAFT -> PUBLISHED is valid
        assert article.can_transition_to(NewsStatus.PUBLISHED) is True
        # DRAFT -> ARCHIVED is not valid
        assert article.can_transition_to(NewsStatus.ARCHIVED) is False

        article.publish()

        # PUBLISHED -> ARCHIVED is valid
        assert article.can_transition_to(NewsStatus.ARCHIVED) is True
        # PUBLISHED -> DRAFT is not valid
        assert article.can_transition_to(NewsStatus.DRAFT) is False

        article.archive()

        # ARCHIVED -> anything is not valid
        assert article.can_transition_to(NewsStatus.PUBLISHED) is False
        assert article.can_transition_to(NewsStatus.DRAFT) is False
