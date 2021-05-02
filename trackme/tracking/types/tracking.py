from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from .meta import Attribute, AttributeOutput


class TrackingActivity(BaseModel):
    id: int
    created_at: datetime
    edit_at: Optional[datetime]
    comment: Optional[str]
    estimation: int
    deleted_at: Optional[datetime]
    topic_id: int
    user_id: int
    attributes: List[AttributeOutput]


class FilterTrackingAttributes(BaseModel):
    starting_time: Optional[str] = None
    ending_time: Optional[str]
    topics: Optional[List[str]] = None
    attributes: Optional[List[str]] = None
    comments: bool = False


class TrackingActivityInput(BaseModel):
    topic_id: int
    comment: Optional[str]
    estimation: int
    attributes: List[Attribute] = Field(default_factory=list, min_items=1)


class UpdateTrackingActivity(BaseModel):
    id: int
    comment: Optional[str]
    delete_attribuets: List[int] = Field(default_factory=list)
    add_attributes: List[Attribute] = Field(default_factory=list)
