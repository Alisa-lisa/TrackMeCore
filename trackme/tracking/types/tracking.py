from typing import Optional
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
