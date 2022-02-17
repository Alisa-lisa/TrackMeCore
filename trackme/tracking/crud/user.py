from typing import Optional, Tuple
import uuid
from sqlalchemy.sql import select
from trackme.tracking.types.user import UserInput
from .user_validation import (
    _get_user,
    get_user_id_by_token,
    # _is_email_valid,
    # _is_valid_name,
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
    """create a new user if possible"""
    async with async_session() as db:
        try:
            db.add(
                UserModel(
                    name=user.name,
                    pwhash=hasher(user),
                    email=user.email,
                    registration=datetime.now(),
                    last_active=datetime.now(),
                )
            )
            await db.commit()
            return True, "success"
        except Exception as ex:
            logger.error(f"Could not save a user due to {ex}")
            return False, f"Error: {ex}"


async def auth_user(user: UserInput) -> Tuple[Optional[str], str]:
    """create new access token or return existing one for existing user"""
    async with async_session() as db:
        verify_user = await _get_user(db, user)
        if verify_user is not None:
            existing_token = (
                (await db.execute(select(UserActivityModel).filter(UserActivityModel.user_id == verify_user.user_id)))
                .scalars()
                .first()
            )
            if existing_token is not None:
                return str(existing_token.token), "success"
            else:
                token = UserActivityModel(
                    user_id=verify_user.user_id,
                    token=uuid.uuid4(),
                    activation=datetime.now(),
                )
                db.add(token)
                await db.commit()
                return str(token.token), "success"
        else:
            logger.error(f"user {user} is not registered in the system")
            return None, "User is unknown"


# update
# async def update_user(update_data: UserOptions, token: str) -> Tuple[bool, str]:
#     """ update some less importnat fields, password update is done separately """
#     async with async_session() as db:
#         try:
#             # get user by token
#             user_id = await get_user_id_by_token(db, token)
#             if user_id is None:
#                 logger.error("User does not exist")
#                 return False, "No user to update"
#             user = (await db.execute(select(UserModel).where(UserModel.id == user_id))).scalars().first()
#             # name and password needs to be updated together always
#             new_name = (
#                 update_data.name
#                 if update_data.name is not None and await _is_valid_name(db, update_data.name)
#                 else user.name
#             )
#             user.name = new_name
#             if update_data.email is not None:
#                 new_email = update_data.email if await _is_email_valid(db, update_data.email) else user.email
#                 user.email = new_email
#             await db.commit()
#             return True, "success"
#         except Exception as ex:
#             logger.error(f"Could not update user due to {ex}")
#             return False, "Update failed"


# delete
async def delete_user(user: UserInput, token: str) -> bool:
    async with async_session() as db:
        try:
            # collect user
            user_to_delete_id = await get_user_id_by_token(db, token)
            user_to_delete = (
                (await db.execute(select(UserModel).where(UserModel.id == user_to_delete_id))).scalars().first()
            )
            # check if name and password are consistent
            is_confirmed = verify(user_to_delete.pwhash, user)
            if is_confirmed:
                await db.delete(user_to_delete)
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Could not delete user due to {ex}")
            return False
