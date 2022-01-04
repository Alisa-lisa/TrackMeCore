from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class MentalBalanceTagEnum(str, Enum):
    chores = "chores"
    social = "social"
    fun = "fun"
    mastery = "mastery"


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
    balance_tag: Optional[MentalBalanceTagEnum]


class TrackingActivityInput(BaseModel):
    topic_id: Optional[int]
    comment: Optional[str]
    estimation: Optional[int]
    attribute: Optional[int]
    # TODO: validate datetime format
    time: Optional[datetime]
    balance_tag: Optional[MentalBalanceTagEnum]

    class Config:
        schema_extra = {
            "example": {
                "topic_id": 1,
                "comment": "neutral mood",
                "estimation": 5,
                "attribute": 1,
                "time": "2021-12-21 12:44:52",
                "balance_tag": "mastery",
            }
        }


class UpdateTrackingActivity(BaseModel):
    id: int
    topic: Optional[int]
    comment: Optional[str]
    attribute: Optional[int]
    # TODO: validate that chosen attribute does belong to topic of older state
    # update of estimate is not allowed at this stage,
    # since this would be the most important information that we want to keep maximally unbiased
