"""[Feature: News Management] Pytest configuration and fixtures."""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.database import Base
from app.core.security import UserContext
from app.domain.entities.news import NewsArticle, NewsScope, NewsStatus
from app.infrastructure.repositories.news_repository import SQLAlchemyNewsRepository


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Use SQLite for testing (simpler, no Docker required)
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db_engine):
    """Create a new database session for each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def repository(db_session):
    """Create a repository instance for testing."""
    return SQLAlchemyNewsRepository(db_session)


@pytest.fixture
def admin_user():
    """Create a mock admin user."""
    return UserContext(user_id=uuid4(), role="ADMIN")


@pytest.fixture
def member_user():
    """Create a mock member user."""
    return UserContext(user_id=uuid4(), role="MEMBER")


@pytest.fixture
def visitor_user():
    """Create a mock visitor user."""
    return UserContext(user_id=uuid4(), role="VISITOR")


@pytest.fixture
def sample_article_data(admin_user):
    """Sample article data for tests."""
    return {
        "title": "Test Article",
        "summary": "Test Summary",
        "content": "<p>Test Content</p>",
        "scope": NewsScope.GENERAL,
        "author_id": admin_user.user_id,
        "cover_url": "https://example.com/image.jpg",
        "tags": ["test", "sample"],
    }


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
