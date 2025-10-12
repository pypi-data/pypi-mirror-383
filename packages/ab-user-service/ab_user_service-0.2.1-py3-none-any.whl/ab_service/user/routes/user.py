"""User-related API routes."""

from typing import Annotated
from uuid import UUID

from ab_core.database.session_context import db_session_async
from ab_core.dependency import Depends
from ab_core.user.model import User
from ab_core.user.service import UserService
from fastapi import APIRouter, HTTPException
from fastapi import Depends as FDepends
from sqlalchemy.ext.asyncio import AsyncSession

from ab_service.user.schema import UpsertByOIDCRequest

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get(
    "/{user_id}",
    response_model=User,
)
async def get_user_by_id(
    user_id: UUID,
    db_session: Annotated[AsyncSession, FDepends(db_session_async)],
    user_service: Annotated[UserService, Depends(UserService, persist=True)],
):
    """Get user by ID."""
    user = await user_service.get_user_by_id(
        user_id=user_id,
        db_session=db_session,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get(
    "/oidc",
    response_model=User,
)
async def get_user_by_oidc(
    oidc_sub: str,
    oidc_iss: str,
    db_session: Annotated[AsyncSession, FDepends(db_session_async)],
    user_service: Annotated[UserService, Depends(UserService, persist=True)],
):
    """Get user by OIDC subject and issuer."""
    user = await user_service.get_user_by_oidc(
        oidc_sub=oidc_sub,
        oidc_iss=oidc_iss,
        db_session=db_session,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "/{user_id}/seen",
    response_model=User,
)
async def seen_user(
    user_id: UUID,
    db_session: Annotated[AsyncSession, FDepends(db_session_async)],
    user_service: Annotated[UserService, Depends(UserService, persist=True)],
):
    """Mark user as seen (update last_seen timestamp)."""
    user = await user_service.get_user_by_id(
        user_id=user_id,
        db_session=db_session,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_service.seen_user(user=user, db_session=db_session)
    return user


@router.put(
    "/oidc",
    response_model=User,
)
async def upsert_user_by_oidc(
    payload: UpsertByOIDCRequest,
    db_session: Annotated[AsyncSession, FDepends(db_session_async)],
    user_service: Annotated[UserService, Depends(UserService, persist=True)],
):
    """Create or update a user based on OIDC info."""
    user = await user_service.upsert_user_by_oidc(
        oidc_sub=payload.oidc_sub,
        oidc_iss=payload.oidc_iss,
        email=payload.email,
        display_name=payload.display_name,
        preferred_username=payload.preferred_username,
        db_session=db_session,
    )
    return user
