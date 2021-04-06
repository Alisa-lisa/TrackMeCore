""" very simple tracking API """
from typing import List, Optional
from fastapi import APIRouter,HTTPException, Header
from trackme.tracking.types import (
        TrackingActivityInput, 
        TrackingActivityOutput,
        TrackingActivityOption,
        Topic,
        Attribute,
        UserInput,
)
from trackme.tracking.crud import (
        simple_track,
        get_user_by_token,
        get_topic_by_id, 
        get_records_for_user,
        get_topics_names,
)
import logging
from fastapi.logger import logger
from fastapi.responses import FileResponse
from datetime import datetime, date
import csv
from typing import List


router = APIRouter()
logger.setLevel(logging.ERROR)


# READ
@router.get("/topics", response_model=List[Topic])
async def get_topics():
    return get_topics_names()


@router.get("/attributes", response_model=List[Attribute])
async def get_attributes(user_id: Optional[int], topic_id: int):
    """ 
    # Collect attributes for specific topic
    ---
    ## Parameters:
    * user_id: optional user id to get custom attributes, if None - collect default attributes
    * topic_id: topic id to identify specific subgroup of attributes

    ## Returns:
    List of attributes. Minimal list will consist of default attributes for the topic
    """
    return get_attributes(user_id, topic_id)


@router.get("/raw")
async def get_raw_data(token: str = Header(None)):
    """ data dump for the user """
    if token is None:
        raise HTTPException(401, "No access token provided")
    user_id = get_user_by_token(token)
    if user_id is None:
        logger.error(f"No user found fr this token")
        raise HTTPException(404, "Not a valid token")
    now = date.today().isoformat()
    file_location = f"{now}_raw.csv"
    try:
        # TODO: put it into separate function
        data = get_records_for_user(user_id)
        data_prepared = [TrackingActivityOutput(timestamp=o.timestamp,
            value=o.value,
            estimate=o.estimate,
            comment=o.comment,
            topic=get_topic_by_id(o.topic_id)).dict() for o in data]
        keys = data_prepared[0].keys()
        with open(file_location, 'w', newline='') as raw:
            writer = csv.DictWriter(raw, fieldnames=keys)
            writer.writeheader()
            for d in data_prepared:
                writer.writerow(d)
            return FileResponse(file_location)
    except Exception as ex:
        logger.error(f"Could not download a file due to {ex}")
        return {"message": "no file can be created at this time."}


# WRITE
@router.post("/save", response_model=bool)
async def track(data_input: TrackingActivityInput, token: str = Header(None)):
    """ unified tracking endpoint - no predefined form """
    if token is None:
        raise HTTPException(401, "No access token provided")
    else:
        user_id = get_user_by_token(token)
        if user_id is None:
            logger.error(f"Could not detect user for token {token}")
            raise HTTPException(404, "Not a valid token")
        return simple_track(data_input, user_id)


# UPDATE
@router.put("/update", response_model=bool)
async def update_entry(data_input: TrackingActivityOption,user_input: UserInput, token: str = Header(None)):
    """
    Adjust specific entry
    ---

    ## Parameters:
    * data_input - all fields of tracking Entry that should be updated must not be None
    * user_input - user name and password to confirm change

    ## Returns:
    If successful True, otherwise False
    """
    return False



# DELETE
@router.delete("/delete", response_model=bool)
async def delete_one_entry(entry_id: int, token: str = Header(None)):
    """
    Delete one specific entry by id
    ---

    ## Parameters:
    * entry_id - id of specific data record to delete

    ## Returns:
    True if successful, False otherwise

    """
    return False


@router.delete("/delete_all", response_model=bool)
async def delete_all_data(user_input: UserInput, token: str = Header(None)):
    """
    Hard delete of all tracking data stored for this user
    ---

    ## Parameters:
    * user_input: name and password to confirm deletion
    
    ## Returns:
    True if successful, False otherwise
    """
    return False
