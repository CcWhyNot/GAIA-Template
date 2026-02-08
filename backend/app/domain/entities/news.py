"""News Management domain entities and value objects."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class NewsStatus(str, Enum):
    """[Feature: News Management] [Story: NM-ADMIN-003] Status of a news article."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class NewsScope(str, Enum):
    """[Feature: News Management] [Story: NM-ADMIN-001] Visibility scope of a news article."""

    GENERAL = "GENERAL"
    INTERNAL = "INTERNAL"


@dataclass
class NewsArticle:
    """[Feature: News Management] [Story: NM-ADMIN-001] Domain entity for a news article."""

    title: str
    summary: str
    content: str
    scope: NewsScope
    author_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: NewsStatus = field(default=NewsStatus.DRAFT)
    cover_url: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    published_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_deleted: bool = False

    def publish(self) -> None:
        """Transition article from DRAFT to PUBLISHED."""
        if self.status != NewsStatus.DRAFT:
            raise ValueError(f"Cannot publish article in {self.status} status")
        self.status = NewsStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Transition article from PUBLISHED to ARCHIVED."""
        if self.status != NewsStatus.PUBLISHED:
            raise ValueError(f"Cannot archive article in {self.status} status")
        self.status = NewsStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Soft delete the article."""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()

    def can_transition_to(self, target_status: NewsStatus) -> bool:
        """Check if article can transition to target status."""
        valid_transitions = {
            NewsStatus.DRAFT: [NewsStatus.PUBLISHED],
            NewsStatus.PUBLISHED: [NewsStatus.ARCHIVED],
            NewsStatus.ARCHIVED: [],
        }
        return target_status in valid_transitions.get(self.status, [])
