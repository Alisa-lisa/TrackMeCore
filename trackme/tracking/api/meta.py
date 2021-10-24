""" Meta data: topics, attributes handling """
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from trackme.tracking.crud import (
    get_topics,
    get_attributes,
    check_user,
    add_attributes,
    delete_attributes,
)
from trackme.tracking.types.meta import Topic, Attribute, AttributeInput
from trackme import conf


router = APIRouter()


@router.get("/topics", response_model=List[Topic])
async def get_topic_names():
    """
    Collect main data topics.
    ---
    For now there are 4 hard-coded topics, in the future it will be possible to add custom topics
    """
    return await get_topics()


@router.get("/attributes", response_model=List[Attribute])
async def get_attributes_names(topic_id: int, token: Optional[str] = Header(None)):
    """
    # Collect attributes for specific topic
    ---
    ## Parameters:
    * token: optional user token to get custom attributes, if None - collect default attributes
    * topic_id: topic id to identify specific subgroup of attributes

    ## Returns:
    List of attributes. Minimal list will consist of default attributes for the topic
    """
    user_id = None
    if token is not None:
        user_id = await check_user(token)
    return await get_attributes(user_id, topic_id)


@router.post("/attributes", response_model=Optional[Attribute])  # type: ignore
async def create_custom_attribute(attribute: AttributeInput, access_token: str = Header(...), token: str = Header(...)):
    """
    # Create a custom attribute for a specified topic
    ---
    ## Parameters:
    * topic_id: id of the topic the Attribute will be created for
    * token: only logged-in users can create topics for themselves
    * name: name of the attribute

    ## Returns:
    Attribute if the creation was successful, otherwise None
    """
    if access_token is not None and access_token == conf.ACCESS_TOKEN:
        user = await check_user(token)
        return await add_attributes(attribute, user)
    raise HTTPException(status_code=401, detail="You are not authorized to access this API")


@router.delete("/attributes", response_model=bool)
async def delete_custom_attribute(attribute_id: int, access_token: str = Header(...), token: str = Header(...)):
    """
    # Delete a custom created attribute
    ---
    ## Parameters:
    * attribute_id - id of the attribute to delete

    ## Returns:
    True if deletion is successful, False otherwise
    """
    if access_token is not None and access_token == conf.ACCESS_TOKEN:
        user = await check_user(token)
        if user is not None:
            return await delete_attributes(attribute_id)
    raise HTTPException(status_code=401, detail="You are not authorized to access this API")
