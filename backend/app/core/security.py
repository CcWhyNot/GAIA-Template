"""[Feature: News Management] Security and authentication utilities."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status


class UserContext:
    """Current user context extracted from JWT or request."""

    def __init__(self, user_id: UUID, role: str):
        self.user_id = user_id
        self.role = role  # ADMIN, MEMBER, SUPPORTER, VISITOR


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[UserContext]:
    """
    [Feature: News Management] Extract current user from Authorization header.

    For development/testing, accepts a simple Bearer token with format:
    Bearer <user_id>:<role>

    In production, this would validate JWT tokens.

    Args:
        authorization: Authorization header.

    Returns:
        UserContext if authenticated, None if not.
    """
    if not authorization:
        return None

    try:
        # Parse Bearer token
        if not authorization.startswith("Bearer "):
            return None

        token = authorization.replace("Bearer ", "").strip()

        # Simple token format: user_id:role
        parts = token.split(":")
        if len(parts) != 2:
            return None

        user_id = UUID(parts[0])
        role = parts[1].upper()

        # Validate role
        if role not in ["ADMIN", "MEMBER", "SUPPORTER", "VISITOR"]:
            return None

        return UserContext(user_id=user_id, role=role)
    except Exception:
        return None


async def require_admin(user: Optional[UserContext] = Depends(get_current_user)):
    """[Feature: News Management] [Story: NM-ADMIN-001] Dependency for Admin-only endpoints."""
    if not user or user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action",
        )
    return user


async def require_authenticated(
    user: Optional[UserContext] = Depends(get_current_user),
):
    """Dependency for authenticated endpoints (any role)."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def get_user_or_none(user: Optional[UserContext] = Depends(get_current_user)):
    """Dependency for endpoints that accept both authenticated and unauthenticated users."""
    return user
