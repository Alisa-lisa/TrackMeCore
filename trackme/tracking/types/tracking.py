from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class Topic(BaseModel):
    class Config:
        orm_mode = True
    id: int
    name: str
   

class Attribute(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    topic_id: int
    user_id: Optional[int]


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
