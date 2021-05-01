""" All about data collections, editing, deletion, download and upload """
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse
from trackme.tracking.types.tracking import (
        TrackingActivityInput,
        UpdateTrackingActivity,
        TrackingActivity,
        FilterTrackingAttributes,
)
from trackme.tracking.types.meta import (
        Topic,
        Attribute,
)
from trackme.tracking.types.user import UserInput
from trackme.tracking.crud import (
        simple_track,
        delete_entry,
        get_user_by_token,
        edit_entry,
        does_entry_exist,
        filter_entries,
)
import logging
from fastapi.logger import logger
from datetime import datetime, date


router = APIRouter()
logger.setLevel(logging.ERROR)

# TODO: Error messages go into middleware validation
NO_TOKEN = "No access token provided"
NO_USER_TOKEN = "Invalid token"
UNKNOWN_ID = "No entry with this id was found"


# TODO: ideally this should go into specific middleware or auth function
async def check_user(token: str) -> int:
    if token is None:
        raise HTTPException(401, NO_TOKEN)
    user_id = await get_user_by_token(token)
    if user_id is None:
        raise HTTPException(404, NO_USER_TOKEN)
    return user_id



# READ

# this should be get -> put filters into query params
@router.post("/data", response_model=List[TrackingActivity])
async def collect_filtered_entries(filter_conditions: FilterTrackingAttributes, token: str = Header(...)):
    """
    # Filter tracking entries 
    ---
    ## Parameters:
    - starting time stamp
    - ending time stamp
    - topics: List[str]
    - comment: bool
    - attributes: List[str]

    ## Returns:
    List of tracking entries satisfying filter conditions, sorted by recency
    """
    user = await check_user(token)
    return await filter_entries(user, filter_conditions.topics, filter_conditions.starting_time, filter_conditions.ending_time, filter_conditions.attributes, filter_conditions.comments)


@router.get("/download")
async def download_data(token: str = Header(...)):
    """
    Collect user data in one file
    """
    return JSONResponse(success=False, error="Not implemented yet")
# async def get_raw_data(token: str = Header(None)):
#     """ data dump for the user """
#     if token is None:
#         raise HTTPException(401, "No access token provided")
#     user_id = get_user_by_token(token)
#     if user_id is None:
#         logger.error(f"No user found fr this token")
#         raise HTTPException(404, "Not a valid token")
#     now = date.today().isoformat()
#     file_location = f"{now}_raw.csv"
#     try:
#         # TODO: put it into separate function
#         data = get_records_for_user(user_id)
#         data_prepared = [TrackingActivityOutput(timestamp=o.timestamp,
#             value=o.value,
#             estimate=o.estimate,
#             comment=o.comment,
#             topic=get_topic_by_id(o.topic_id)).dict() for o in data]
#         keys = data_prepared[0].keys()
#         with open(file_location, 'w', newline='') as raw:
#             writer = csv.DictWriter(raw, fieldnames=keys)
#             writer.writeheader()
#             for d in data_prepared:
#                 writer.writerow(d)
#             return FileResponse(file_location)
#     except Exception as ex:
#         logger.error(f"Could not download a file due to {ex}")
#         return {"message": "no file can be created at this time."}
#
#
# WRITE
@router.post("/save", response_model=bool)
async def track(data_input: TrackingActivityInput, token: str = Header(...)):
    """ 
    Save tracking entry
    ---
    ## Parameters:
    - data_input: TrackingActivityInput
    - token for user identification
    
    ## Returns:
    True if operation is successful, False otherwise
    """
    if token is None:
        raise HTTPException(401, NO_TOKEN)
    user_id = await get_user_by_token(token)
    if user_id is None:
        raise HTTPException(404, NO_USER_TOKEN)
    return await simple_track(data_input.topic_id, data_input.comment, data_input.estimation, data_input.attributes, user_id)


@router.put("/update", response_model=bool)
async def update_entry(data_input: UpdateTrackingActivity, token: str = Header(None)):
    """
    Adjust specific entry
    ---

    ## Parameters:
    * data_input - all fields of tracking Entry that should be updated must not be None
    * user_input - user name and password to confirm change

    ## Returns:
    True if successful, False otherwise
    """
    if token is None:
        raise HTTPException(401, NO_TOKEN)
    user_id = await get_user_by_token(token)
    if user_id is None:
        raise HTTPException(404, NO_USER_TOKEN)
    if not (await does_entry_exist(data_input.id)):
        raise HTTPException(400, UNKNOWN_ID)
    return await edit_entry(user_id, data_input.id, data_input.comment, data_input.delete_attribuets, data_input.add_attributes)



# DELETE
@router.delete("/delete", response_model=bool)
async def delete_entries(entry_ids: List[int], token: str = Header(...)):
    """
    Delete one specific entry by id
    ---

    ## Parameters:
    * entry_id - id of specific data record to delete

    ## Returns:
    True if successful, False otherwise

    """
    if token is None:
        raise HTTPException(401, NO_TOKEN)
    user_id = await get_user_by_token(token)
    if user_id is None:
        raise HTTPException(404, NO_USER_TOKEN)
    return await delete_entry(entry_ids, user_id)
