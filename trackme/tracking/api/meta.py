""" Meta data: topics, attributes handling """
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse

from trackme.tracking.crud import (
   get_topics,
   get_attributes,
)
import logging
from fastapi.logger import logger

from trackme.tracking.types.meta import (
        Topic,
        Attribute,
)

router = APIRouter()
logger.setLevel(logging.ERROR)


@router.get("/topics", response_model=List[Topic])
async def get_topic_names():
    """
    Collect main data topics.
    ---
    For now there are 4 hard-coded topics, in the future it will be possible to add custom topics
    """
    return await get_topics()


@router.get("/attributes", response_model=List[Attribute])
async def get_attributes_names(topic_id: int, user_id: Optional[int] = None):
    """ 
    # Collect attributes for specific topic
    ---
    ## Parameters:
    * user_id: optional user id to get custom attributes, if None - collect default attributes
    * topic_id: topic id to identify specific subgroup of attributes

    ## Returns:
    List of attributes. Minimal list will consist of default attributes for the topic
    """
    return await get_attributes(user_id, topic_id)


