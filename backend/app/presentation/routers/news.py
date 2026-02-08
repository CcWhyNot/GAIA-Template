"""[Feature: News Management] FastAPI router for news articles."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.use_cases.change_news_status import ChangeNewsStatusUseCase
from app.application.use_cases.create_news import CreateNewsUseCase
from app.application.use_cases.delete_news import DeleteNewsUseCase
from app.application.use_cases.get_news_detail import GetNewsDetailUseCase
from app.application.use_cases.list_news import ListNewsUseCase
from app.application.use_cases.update_news import UpdateNewsUseCase
from app.core.database import get_db
from app.core.security import (
    UserContext,
    get_user_or_none,
    require_admin,
)
from app.domain.entities.news import NewsScope, NewsStatus
from app.infrastructure.repositories.news_repository import SQLAlchemyNewsRepository
from app.presentation.schemas.news import (
    ChangeStatusRequest,
    CreateNewsRequest,
    NewsCardResponse,
    NewsResponse,
    PaginatedNewsResponse,
    UpdateNewsRequest,
)

router = APIRouter(prefix="/api/v1/news", tags=["news"])


@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    request: CreateNewsRequest,
    admin: UserContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    [Feature: News Management] [Story: NM-ADMIN-001] Create a new news article.

    Only Administrators can create articles.
    """
    try:
        repository = SQLAlchemyNewsRepository(db)
        use_case = CreateNewsUseCase(repository)

        article = await use_case.execute(
            title=request.title,
            summary=request.summary,
            content=request.content,
            scope=request.scope,
            author_id=admin.user_id,
            cover_url=request.cover_url,
            tags=request.tags,
        )

        return NewsResponse.model_validate(article.__dict__)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/{article_id}", response_model=NewsResponse)
async def update_news(
    article_id: UUID,
    request: UpdateNewsRequest,
    admin: UserContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    [Feature: News Management] [Story: NM-ADMIN-002] Update a news article.

    Only Administrators can update articles.
    """
    try:
        repository = SQLAlchemyNewsRepository(db)
        use_case = UpdateNewsUseCase(repository)

        article = await use_case.execute(
            article_id=article_id,
            title=request.title,
            summary=request.summary,
            content=request.content,
            scope=request.scope,
            cover_url=request.cover_url,
            tags=request.tags,
        )

        return NewsResponse.model_validate(article.__dict__)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch("/{article_id}/status", response_model=NewsResponse)
async def change_news_status(
    article_id: UUID,
    request: ChangeStatusRequest,
    admin: UserContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    [Feature: News Management] [Story: NM-ADMIN-003] Change article status.

    Valid transitions: DRAFT -> PUBLISHED, PUBLISHED -> ARCHIVED
    """
    try:
        repository = SQLAlchemyNewsRepository(db)
        use_case = ChangeNewsStatusUseCase(repository)

        article = await use_case.execute(
            article_id=article_id,
            target_status=request.status,
        )

        return NewsResponse.model_validate(article.__dict__)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        else:
            # Invalid transition
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg,
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/{article_id}", status_code=status.HTTP_200_OK)
async def delete_news(
    article_id: UUID,
    admin: UserContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    [Feature: News Management] [Story: NM-ADMIN-004] Soft delete a news article.

    Only Administrators can delete articles.
    """
    try:
        repository = SQLAlchemyNewsRepository(db)
        use_case = DeleteNewsUseCase(repository)

        await use_case.execute(article_id=article_id, admin_user_id=admin.user_id)

        return {
            "message": "Article deleted successfully",
            "article_id": str(article_id),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{article_id}", response_model=NewsResponse)
async def get_news_detail(
    article_id: UUID,
    user: UserContext = Depends(get_user_or_none),
    db: Session = Depends(get_db),
):
    """
    [Feature: News Management] [Story: NM-MEMBER-001] Get news article detail.

    Scope-based visibility:
    - Members see GENERAL + INTERNAL published articles
    - Visitors/Supporters see only GENERAL published articles
    - INTERNAL articles return 404 for non-members (no info disclosure)
    """
    try:
        repository = SQLAlchemyNewsRepository(db)
        use_case = GetNewsDetailUseCase(repository)

        user_role = user.role if user else "VISITOR"

        article = await use_case.execute(article_id=article_id, user_role=user_role)

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found",
            )

        return NewsResponse.model_validate(article.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("", response_model=PaginatedNewsResponse)
async def list_news(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum articles to return"),
    q: str = Query("", description="Search query (title or summary)"),
    scope: str = Query(
        None, description="Filter by scope (GENERAL or INTERNAL, Members only)"
    ),
    user: UserContext = Depends(get_user_or_none),
    db: Session = Depends(get_db),
):
    """
    [Feature: News Management] [Story: NM-VISITOR-002] List published news articles.

    Role-based filtering:
    - Visitors/Supporters see only GENERAL articles
    - Members see GENERAL + INTERNAL articles
    - Admins see all statuses

    Supports pagination, search, and scope filtering.
    """
    try:
        repository = SQLAlchemyNewsRepository(db)
        use_case = ListNewsUseCase(repository)

        user_role = user.role if user else "VISITOR"

        # Parse scope filter (for Members only)
        scope_filter = None
        if scope:
            try:
                scope_filter = NewsScope[scope.upper()]
                # Only Members can filter by INTERNAL scope
                if scope_filter == NewsScope.INTERNAL and user_role != "MEMBER":
                    scope_filter = None
            except KeyError:
                pass

        articles, total_count = await use_case.execute(
            skip=skip,
            limit=limit,
            search_query=q if q else None,
            scope_filter=scope_filter,
            user_role=user_role,
        )

        items = [NewsCardResponse.model_validate(a.__dict__) for a in articles]

        return PaginatedNewsResponse(
            items=items,
            total=total_count,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
