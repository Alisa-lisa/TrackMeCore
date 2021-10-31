from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class TrackingActivity(BaseModel):
    id: int
    created_at: datetime
    edit_at: Optional[datetime]
    comment: Optional[str]
    estimation: Optional[int]
    deleted_at: Optional[datetime]
    topic_id: Optional[int]
    user_id: int
    attribute: str


class TrackingActivityInput(BaseModel):
    topic_id: Optional[int]
    comment: Optional[str]
    estimation: Optional[int]
    attribute: Optional[int]
    time: Optional[datetime]


class UpdateTrackingActivity(BaseModel):
    id: int
    topic: Optional[int]
    comment: Optional[str]
    attribute: Optional[int]
    # TODO: validate that chosen attribute does belong to topic of older state
    # update of estimate is not allowed at this stage,
    # since this would be the most important information that we want to keep maximally unbiased
