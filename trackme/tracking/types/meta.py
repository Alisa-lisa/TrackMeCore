from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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
    icon_name: Optional[str]
    active: bool


class AttributeUpdateInput(BaseModel):
    id: int
    active: Optional[bool]
    # name: Optional[str]
    # icon_name: Optional[str]


class AttributeInput(BaseModel):
    name: str
    topic_id: int
    icon_name: str


class AttributeOutput(BaseModel):
    name: str
    active: bool


class Experiment(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: Optional[str]
    created_at: datetime
    closed_at: Optional[datetime]
    user_id: int


class ExperimentInput(BaseModel):
    name: str


class ExperimentUpdateInput(BaseModel):
    id: int
    name: Optional[str]
    closed_at: Optional[datetime]
