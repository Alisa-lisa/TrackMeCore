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


class AttributeOutput(BaseModel):
    name: str
