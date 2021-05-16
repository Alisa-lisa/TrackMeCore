from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Header
from trackme.tracking.types.user import (
    UserInput,
)
from trackme.tracking.crud import (
    create_user,
    auth_user,
    delete_user,
)
from fastapi.logger import logger
import logging


router = APIRouter()
logger.setLevel(logging.ERROR)


@router.post("/register", response_model=bool)
async def register_user(input_user: UserInput):
    """user registration"""
    status, message = await create_user(input_user)
    if not status:
        raise HTTPException(400, message)
    return status


@router.post("/auth", response_model=str)
async def login_user(input_user: UserInput):
    """either refresh an access token or fetch already existing one"""
    token, message = await auth_user(input_user, None, None)
    if token is None:
        raise HTTPException(403, message)
    return token


# @router.put("/update", response_model=bool)
# async def update_user(input_update: UserOptions, token: str = Header(None)):
#     """
#     Update some user information
#     ---
#
#     ## Parameters:
#
#
#     ## Returns:
#
#     """
#     success, message = await edit_user(input_update, token)
#     if not success:
#         raise HTTPException(400, message)
#     return True
#


@router.delete("/delete", response_model=bool)
async def remove_user(input_user: UserInput, token: str = Header(None)):
    """user should be able to delete himself form the platform"""
    return await delete_user(input_user, token)
