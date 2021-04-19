from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator


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
