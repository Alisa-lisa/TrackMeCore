from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime

from .data_type import Attribute


class TrackingActivity(BaseModel):
    id: int
    created_at: datetime
    edit_at: Optional[datetime]
    comment: Optional[str]
    estimation: int
    deleted_at: Optional[datetime]
    topic_id: int
    user_id: int
    attributes: List[Attribute]

    class Config:
        orm_mode = True


class TrackingActivityInput(BaseModel):
    topic_id: int
    comment: Optional[str]
    estimation: int
    attributes: List[Attribute] = Field(default_factory=list, min_items=1)


class UpdateTrackingActivity(BaseModel):
    id: int
    comment: Optional[str]
    delete_attribuets: List[Attribute] = Field(default_factory=list)
    add_attributes: List[Attribute] = Field(default_factory=list)
