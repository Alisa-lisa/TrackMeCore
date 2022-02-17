from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import uuid


class UserInput(BaseModel):
    name: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = Field(None)


class UserOutput(BaseModel):
    name: str
    user_id: int


class UserOptions(BaseModel):
    name: Optional[str]
    # password: Optional[str]
    email: Optional[str]


class UserActivity(BaseModel):
    user_id: int
    token: uuid.UUID
    activation: datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    name: str
    pwhash: str
    email: str
    registration: datetime
    last_active: Optional[datetime] = None
    activity: List[UserActivity]

    class Config:
        orm_mode = True
