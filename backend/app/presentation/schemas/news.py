"""[Feature: News Management] [Story: NM-ADMIN-001] Pydantic schemas for news articles."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.domain.entities.news import NewsScope, NewsStatus


class CreateNewsRequest(BaseModel):
    """[Feature: News Management] [Story: NM-ADMIN-001] Request DTO for creating a news article."""

    title: str = Field(..., min_length=1, max_length=255, description="Article title")
    summary: str = Field(
        ..., min_length=1, max_length=500, description="Article summary"
    )
    content: str = Field(..., min_length=1, description="Article HTML content")
    scope: NewsScope = Field(..., description="Visibility scope (GENERAL or INTERNAL)")
    cover_url: Optional[str] = Field(None, description="Optional cover image URL")
    tags: Optional[List[str]] = Field(
        default_factory=list, description="Optional list of tags"
    )

    class Config:
        extra = "forbid"  # Reject extra fields


class UpdateNewsRequest(BaseModel):
    """[Feature: News Management] [Story: NM-ADMIN-002] Request DTO for updating a news article."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    scope: Optional[NewsScope] = None
    cover_url: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config:
        extra = "forbid"


class ChangeStatusRequest(BaseModel):
    """[Feature: News Management] [Story: NM-ADMIN-003] Request DTO for changing article status."""

    status: NewsStatus = Field(..., description="Target status (PUBLISHED or ARCHIVED)")

    class Config:
        extra = "forbid"


class NewsResponse(BaseModel):
    """[Feature: News Management] [Story: NM-ADMIN-001] Response DTO for a news article."""

    id: UUID
    title: str
    summary: str
    content: str
    status: NewsStatus
    scope: NewsScope
    author_id: UUID
    cover_url: Optional[str] = None
    tags: List[str] = []
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True


class NewsCardResponse(BaseModel):
    """[Feature: News Management] [Story: NM-VISITOR-002] Compact response for list views."""

    id: UUID
    title: str
    summary: str
    cover_url: Optional[str] = None
    published_at: Optional[datetime] = None
    scope: NewsScope
    tags: List[str] = []

    class Config:
        from_attributes = True


class PaginatedNewsResponse(BaseModel):
    """[Feature: News Management] [Story: NM-VISITOR-002] Paginated list response."""

    items: List[NewsCardResponse]
    total: int = Field(..., description="Total number of articles")
    skip: int = Field(..., description="Number of articles skipped")
    limit: int = Field(..., description="Maximum articles per page")

    @property
    def has_more(self) -> bool:
        """Check if there are more articles."""
        return (self.skip + self.limit) < self.total
