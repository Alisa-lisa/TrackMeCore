""" All about data collections, editing, deletion, download and upload """
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from trackme.tracking.types.tracking import (
    TrackingActivityInput,
    UpdateTrackingActivity,
    TrackingActivity,
)
from trackme.tracking.crud import (
    check_user,
    simple_track,
    delete_entry,
    edit_entry,
    does_entry_exist,
    filter_entries,
)
import logging
from fastapi.logger import logger


router = APIRouter()
logger.setLevel(logging.ERROR)

UNKNOWN_ID = "No entry with this id was found"


# READ
@router.get("/filter", response_model=List[TrackingActivity])
async def collect_filtered_entries(
    start: Optional[str] = None,
    end: Optional[str] = None,
    topics: Optional[int] = None,
    attributes: Optional[int] = None,
    comments: bool = False,
    token: str = Header(...),
):
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
    return await filter_entries(user, topics, start, end, attributes, comments)


@router.get("/download", response_model=bool)
async def download_data(token: str = Header(...)):
    """
    Collect user data in one file
    """
    return False


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
    user_id = await check_user(token)
    return await simple_track(
        data_input.topic_id, data_input.comment, data_input.estimation, data_input.attributes, user_id
    )


# TODO: return updated model instead of a bool
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
    user_id = await check_user(token)
    entry_id = await does_entry_exist(data_input.id)
    if not entry_id:
        raise HTTPException(404, "Entry does not exist")
    return await edit_entry(
        user_id, data_input.id, data_input.comment, data_input.delete_attribuets, data_input.add_attributes
    )


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
    user_id = await check_user(token)
    return await delete_entry(entry_ids, user_id)
