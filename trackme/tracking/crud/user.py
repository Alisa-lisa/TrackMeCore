from enum import unique

from sqlalchemy import exc
from trackme.tracking.types.user import UserOptions
from typing import Optional, Tuple
import uuid
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import select 
from trackme.tracking.types import (
        UserInput,
        UserOutput, 
)
from trackme.tracking.models import (
    UserModel,
    UserActivityModel,
)
from trackme.tracking.helpers.hashing import hasher, verify
from datetime import datetime
from fastapi.logger import logger
from trackme.storage import async_session


# create
async def create_user(user: UserInput) -> Tuple[bool, str]:
    """ create a new user if possible """
    async with async_session() as db:
        try:
            db.add(UserModel(name=user.name, 
            pwhash=hasher(user),
            email=user.email,
            registration=datetime.now(),
            last_active=datetime.now()))
            await db.commit()
            return True, "success"
        except Exception as ex:
            logger.error(f"Could not save a user due to {ex}")
            return False, f"Error: {ex}"


async def auth_user(user: UserInput, 
        client: Optional[str], ip: Optional[str]) -> Tuple[Optional[str], str]:
    """ create new access token or return existing one for existing user """
    async with async_session() as db:
        verify_user = await _get_user(db, user)

        if verify_user is not None:
            existing_token = (await db.execute(select(UserActivityModel)\
                    .filter(UserActivityModel.user_id == verify_user.user_id)\
                    .filter(UserActivityModel.client == client))).scalars().first()
            if existing_token is not None:
                return str(existing_token.token), "success"
            else:
                token = UserActivityModel(
                        user_id=verify_user.user_id,
                        token=uuid.uuid4(),
                        activation=datetime.now(),
                        ip=ip,
                        client=client)
                db.add(token)
                await db.commit()
                return str(token.token), "success"
        else:
            logger.error(f"user {user} is not registered in the system")
            return None, "User is unknown"


# read
async def _get_user(db: AsyncSession, user: UserInput) -> Optional[UserOutput]:
    try:
        existing_user = (await db.execute(select(UserModel).where(UserModel.name == user.name))).first()[0]
        if existing_user is not None and verify(existing_user, user):
            return UserOutput(name=existing_user.name, 
                    user_id=existing_user.id)
        else:
            return None
    except Exception as ex:
        logger.error(f"Could not find user due to {ex}")
        return None


async def _get_user_id_by_token(db: AsyncSession, token: str) -> Optional[int]:
    user_id = (await db.execute(select(UserActivityModel.user_id)\
    .where(UserActivityModel.token == token))).first()
    if user_id is None:
        return None   
    return user_id


async def get_user_by_token(token: str) -> Optional[int]:
    async with async_session() as db:
        user_id = await _get_user_id_by_token(db, token)    
        return user_id[0] if user_id is not None else None



async def _is_valid_name(db: AsyncSession, new_name: str) -> bool:
    unique_name = (await db.execute(select(UserModel).where(UserModel.name == new_name))).first()
    if unique_name is not None:
        return False
    return True


async def _is_email_valid(db: AsyncSession, email: str) -> bool:
    unique_email = (await db.execute(select(UserModel).where(UserModel.email == email))).first()
    if unique_email is not None:
        return False
    return True


# update
async def update_user(update_data: UserOptions, token: str) -> Tuple[bool, str]:
    async with async_session() as db:
        try:
            # get user by token
            user_id = await _get_user_id_by_token(db, token)
            if user_id is None:
                logger.error(f"Such user does not exist")
                return False, "No user to update"
            user = (await db.execute(select(UserModel).where(UserModel.id == user_id))).first()[0]
            new_name = update_data.name if update_data.name is not None and await _is_valid_name(db, update_data.name) else user.name
            user.name = new_name
            if update_data.password is not None:
                user.pwhash = hasher(UserInput(name=new_name, password=update_data.password))
            if update_data.email is not None:
                new_email = update_data.email if await _is_email_valid(db, update_data.email) else user.email
                user.email = new_email
            await db.commit()
            return True, "success"
        except Exception as ex:
            logger.error(f"Could not update user due to {ex}")
            return False, "Update failed"


# delete
async def delete_user(user: UserInput) -> bool:
    return False

