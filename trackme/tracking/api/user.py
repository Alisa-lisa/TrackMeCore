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
from trackme import conf

router = APIRouter()
logger.setLevel(logging.ERROR)


@router.post("/register", response_model=bool)
async def register_user(input_user: UserInput, access_token: str = Header(...)):
    """user registration"""
    if access_token is not None and access_token == conf.ACCESS_TOKEN:
        status, message = await create_user(input_user)
        if not status:
            raise HTTPException(status_code=400, detail="Failed to create user")
        return status
    raise HTTPException(status_code=401, detail="You are not authorized to access this API")


@router.post("/auth", response_model=str)
async def login_user(input_user: UserInput, access_token: str = Header(...)):
    """either refresh an access token or fetch already existing one"""
    if access_token is not None and access_token == conf.ACCESS_TOKEN:
        token, message = await auth_user(input_user, None, None)
        if token is None:
            raise HTTPException(403, message)
        return token
    raise HTTPException(status_code=401, detail="You are not authorized to access this API")


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
#     success, message = await edit_user(input_update, tokens
#     if not success:
#         raise HTTPException(400, message)
#     return True
#


@router.delete("/delete", response_model=bool)
async def remove_user(input_user: UserInput, token: str = Header(None), access_token: str = Header(...)):
    """user should be able to delete himself form the platform"""
    if access_token is not None and access_token == conf.ACCESS_TOKEN:
        if token is None:
            raise HTTPException(403, "Unknown user")
        # TODO:  use UserInput as confirmation for deletion action
        return await delete_user(input_user, token)
    raise HTTPException(status_code=401, detail="You are not authorized to access this API")
