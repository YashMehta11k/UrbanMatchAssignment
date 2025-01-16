from pydantic import BaseModel,EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: EmailStr
    city: str
    interests: List[str]

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class MatchResponse(BaseModel):
    user_id: int
    name: str
    age: int
    gender: str
    city: str
    interests: List[str]
    compatibility_score: float