from typing import Optional
from sqlalchemy.ext.asyncio.session import AsyncSession

from fastapi import HTTPException
from trackme.tracking.types.user import UserInput, UserOutput
from trackme.tracking.models import (
    UserModel,
    UserActivityModel,
)
from trackme.tracking.helpers.hashing import verify
from fastapi.logger import logger
from sqlalchemy.sql import select

from trackme.storage import async_session


# TODO: Error messages go into middleware validation
NO_TOKEN = "No access token provided"
NO_USER_TOKEN = "Invalid token"


# TODO: ideally this should go into specific middleware or auth function
async def check_user(token: str) -> int:
    if token is None:
        raise HTTPException(401, NO_TOKEN)
    user_id = await get_user(token)
    if user_id is None:
        raise HTTPException(404, NO_USER_TOKEN)
    return user_id


async def _get_user(db: AsyncSession, user: UserInput) -> Optional[UserOutput]:
    try:
        existing_user = (
            (await db.execute(select(UserModel).where(UserModel.name == user.name)))
            .scalars()
            .first()
        )
        if existing_user is not None and verify(existing_user.pwhash, user):
            return UserOutput(name=existing_user.name, user_id=existing_user.id)
        else:
            return None
    except Exception as ex:
        logger.error(f"Could not find user due to {ex}")
        return None


async def get_user(token: str) -> Optional[int]:
    async with async_session() as db:
        return await get_user_id_by_token(db, token)


async def get_user_id_by_token(db: AsyncSession, token: str) -> Optional[int]:
    user = (
        (
            await db.execute(
                select(UserActivityModel).where(UserActivityModel.token == token)
            )
        )
        .scalars()
        .first()
    )
    return user.user_id if user is not None else None


async def _is_valid_name(db: AsyncSession, new_name: str) -> bool:
    unique_name = (
        await db.execute(select(UserModel).where(UserModel.name == new_name))
    ).first()
    if unique_name is not None:
        return False
    return True


async def _is_email_valid(db: AsyncSession, email: str) -> bool:
    unique_email = (
        await db.execute(select(UserModel).where(UserModel.email == email))
    ).first()
    if unique_email is not None:
        return False
    return True
