"""User-related API routes."""

from typing import Annotated

from ab_core.database.session_context import db_session_async
from ab_core.identity_context.dependency import IdentityContext, get_identity_context
from fastapi import APIRouter
from fastapi import Depends as FDepends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/identity-context", tags=["Identity Context"])


@router.get("", response_model=IdentityContext)
async def me(
    _db_session: Annotated[AsyncSession, FDepends(db_session_async)],
    identity_context: Annotated[IdentityContext, FDepends(get_identity_context)],
):
    """Return the current user's identity context."""
    return identity_context
